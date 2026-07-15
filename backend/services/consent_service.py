"""
The Consent Service.

Every read of patient data goes through here. Not most reads — every read.

An important design choice: allergies and blood group are NEVER gated. There is
no consent framework on earth that requires withholding a penicillin allergy
from a system about to recommend an antibiotic. Some data is safety-critical,
and gating it would kill people.
"""

from datetime import datetime

from extensions import db
from models import AuditEntry, ConsentGrant, ConsentPurpose, ConsentScope


class ConsentService:
    # Safety-critical. Never gated, in any purpose, ever.
    ALWAYS_PERMITTED = {
        ConsentScope.ALLERGIES.value,
        ConsentScope.BLOOD_GROUP.value,
    }

    def get_grant(self, user_id, scope, purpose="triage"):
        """Fetch an active grant. Returns None if absent, revoked, or expired."""
        scope = scope.value if hasattr(scope, "value") else scope
        purpose = purpose.value if hasattr(purpose, "value") else purpose

        grant = (
            ConsentGrant.query.filter_by(
                user_id=user_id, scope=scope, purpose=purpose, revoked=False
            )
            .order_by(ConsentGrant.granted_at.desc())
            .first()
        )

        if not grant:
            return None

        if grant.expires_at and grant.expires_at < datetime.utcnow():
            return grant  # returned so the caller can say WHY it failed

        grant.touch()
        db.session.commit()
        return grant

    def active_scopes(self, user_id, purpose="triage"):
        """Everything currently readable for this purpose."""
        purpose = purpose.value if hasattr(purpose, "value") else purpose

        grants = ConsentGrant.query.filter_by(
            user_id=user_id, purpose=purpose, revoked=False
        ).all()

        scopes = [g.scope for g in grants if g.active]
        return list(set(scopes) | self.ALWAYS_PERMITTED)

    def grant(self, user_id, scope, purpose, grantee=None, grantee_type="omnicare", days=30):
        g = ConsentGrant.grant(
            user_id=user_id,
            scope=scope,
            purpose=purpose,
            grantee=grantee,
            grantee_type=grantee_type,
            days=days,
        )
        db.session.add(g)
        self.audit(user_id, "user", "consent_granted", g.scope, True,
                   f"Granted to {grantee or 'OmniCare'} for {days} days")
        db.session.commit()
        return g

    def revoke(self, user_id, grant_id, reason=None):
        """
        Revoke. Propagates immediately — the next agent check will fail.

        This is the demo moment. A judge asks "what if I change my mind?" and
        you revoke a grant in front of them, re-run the triage, and the Records
        agent doesn't run.
        """
        g = ConsentGrant.query.filter_by(id=grant_id, user_id=user_id).first()
        if not g:
            return None

        g.revoke(reason)
        self.audit(user_id, "user", "consent_revoked", g.scope, False,
                   reason or "Revoked by user")
        db.session.commit()
        return g

    def ledger(self, user_id):
        """Everything, granted and revoked. The patient's own view of who has what."""
        grants = (
            ConsentGrant.query.filter_by(user_id=user_id)
            .order_by(ConsentGrant.granted_at.desc())
            .all()
        )
        return [g.to_dict() for g in grants]

    def audit_trail(self, user_id, limit=100):
        entries = (
            AuditEntry.query.filter_by(user_id=user_id)
            .order_by(AuditEntry.at.desc())
            .limit(limit)
            .all()
        )
        return [e.to_dict() for e in entries]

    def audit(self, user_id, actor, action, scope, granted, reason):
        db.session.add(
            AuditEntry(
                user_id=user_id,
                actor=actor,
                action=action,
                scope=scope,
                granted=granted,
                reason=reason,
            )
        )

    # ── Adapter for the ai/ layer ─────────────────────────────────
    # The ConsentAgent calls .record(); the service speaks .audit().

    def record(self, user_id, actor, action, scope, granted, reason, at=None):
        self.audit(user_id, actor, action, scope, granted, reason)
        db.session.commit()

    @staticmethod
    def bootstrap(user_id):
        """
        Seed the default grants a new user needs to use the product at all.

        30 days, triage purpose, OmniCare as grantee. Explicit, scoped, expiring.
        Not "I agree to the terms."
        """
        defaults = [
            ConsentScope.MEDICAL_HISTORY,
            ConsentScope.LIFESTYLE,
            ConsentScope.VITALS,
            ConsentScope.REPORTS,
        ]
        for scope in defaults:
            db.session.add(
                ConsentGrant.grant(
                    user_id=user_id,
                    scope=scope,
                    purpose=ConsentPurpose.TRIAGE,
                    grantee="OmniCare",
                    grantee_type="omnicare",
                    days=30,
                )
            )
        db.session.commit()
