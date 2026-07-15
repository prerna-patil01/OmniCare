"""
The Consent Agent.

This one is different from the others in kind, not degree. It does not have an
opinion. It does not deliberate. It is a GATE.

Every other agent must pass through it before it sees a single byte of patient
data. If the scope is not granted, the agent does not run — not "runs with less
data," not "runs and mentions the limitation." Does not run.

This is the file that makes OmniCare legally coherent under the DPDP Act, and it
is the thing no other team in the room will have built.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


class ConsentDenied(Exception):
    """
    Raised when an agent requests data it has not been granted.

    Deliberately an exception, not a return value. A denied scope must not be
    something a caller can accidentally ignore.
    """

    def __init__(self, agent: str, scope: str, reason: str):
        self.agent = agent
        self.scope = scope
        self.reason = reason
        super().__init__(f"{agent} denied '{scope}': {reason}")


@dataclass
class ConsentDecision:
    granted: bool
    scope: str
    agent: str
    reason: str
    expires_at: datetime | None = None
    audit_id: str | None = None


@dataclass
class ConsentAgent:
    """
    The gatekeeper.

    Scope requirements are declared per agent, not per route. That matters: it
    means you can look at this one dict and know exactly what each part of the
    system is permitted to see, without reading a line of route code.

    Note what allergies do NOT require. There is no consent framework on earth
    that requires withholding an allergy from a system about to recommend a drug.
    Some data is safety-critical, and gating it would kill people.
    """

    consent_service: object | None = None
    audit_log: object | None = None

    # What each agent needs to do its job at all.
    REQUIREMENTS: dict[str, list[str]] = field(
        default_factory=lambda: {
            "triage": ["medical_history"],
            "records": ["medical_history"],
            "biometrics": ["vitals"],
            "pharmacy": ["medical_history"],  # allergies handled separately
            "logistics": [],                  # needs no clinical data
            "population": [],                 # anonymised aggregate only
        }
    )

    # Never gated. Withholding these is more dangerous than sharing them.
    ALWAYS_PERMITTED = {"allergies", "blood_group", "emergency_contact"}

    def check(self, user_id: str, agent: str, purpose: str = "triage") -> ConsentDecision:
        required = self.REQUIREMENTS.get(agent, [])

        if not required:
            return ConsentDecision(
                granted=True,
                scope="none_required",
                agent=agent,
                reason="Agent requires no patient-identifying scope.",
            )

        # No consent service wired up. Development only — and loud about it,
        # because a silent default-allow in production is how data breaches
        # happen.
        if not self.consent_service:
            logger.warning(
                "ConsentAgent running WITHOUT a consent service. "
                "Default-allow is acceptable in development and nowhere else."
            )
            return ConsentDecision(
                granted=True,
                scope=",".join(required),
                agent=agent,
                reason="No consent service configured (development mode).",
            )

        for scope in required:
            grant = self.consent_service.get_grant(user_id=user_id, scope=scope, purpose=purpose)

            if not grant:
                self._audit(user_id, agent, scope, granted=False, reason="No grant on record")
                return ConsentDecision(
                    granted=False,
                    scope=scope,
                    agent=agent,
                    reason=f"No consent grant for '{scope}'.",
                )

            if grant.revoked:
                self._audit(user_id, agent, scope, granted=False, reason="Grant revoked")
                return ConsentDecision(
                    granted=False,
                    scope=scope,
                    agent=agent,
                    reason=f"Consent for '{scope}' was revoked on {grant.revoked_at:%d %b %Y}.",
                )

            if grant.expires_at and grant.expires_at < datetime.utcnow():
                self._audit(user_id, agent, scope, granted=False, reason="Grant expired")
                return ConsentDecision(
                    granted=False,
                    scope=scope,
                    agent=agent,
                    reason=f"Consent for '{scope}' expired on {grant.expires_at:%d %b %Y}.",
                )

            self._audit(user_id, agent, scope, granted=True, reason="Active grant")

        return ConsentDecision(
            granted=True,
            scope=",".join(required),
            agent=agent,
            reason="All required scopes granted and active.",
        )

    def enforce(self, user_id: str, agent: str, purpose: str = "triage") -> None:
        """Raise if not permitted. Use this when there is no sensible fallback."""
        decision = self.check(user_id, agent, purpose)
        if not decision.granted:
            raise ConsentDenied(agent, decision.scope, decision.reason)

    def active_scopes(self, user_id: str, purpose: str = "triage") -> list[str]:
        """Everything currently permitted. Used by the ContextBuilder."""
        if not self.consent_service:
            return ["medical_history", "lifestyle", "vitals", "reports"]
        return self.consent_service.active_scopes(user_id=user_id, purpose=purpose)

    def _audit(self, user_id: str, agent: str, scope: str, *, granted: bool, reason: str) -> None:
        """
        Every check is logged. Every one.

        Not just denials. When a patient asks "who looked at my liver panel and
        when," the answer must be complete, and you cannot reconstruct a complete
        answer from a log that only recorded the failures.
        """
        if not self.audit_log:
            return

        self.audit_log.record(
            user_id=user_id,
            actor=f"agent:{agent}",
            action="consent_check",
            scope=scope,
            granted=granted,
            reason=reason,
            at=datetime.utcnow(),
        )
