"""
The Adjudicator.

Reads six independent opinions and decides what OmniCare actually says — with
abstention as a first-class outcome, not a fallback.

The design claim here is simple and, I think, correct: a system that resolves
every disagreement is not resolving them, it is hiding them. Averaging away a
30% chance of a heart attack does not make it go away. It just means nobody
mentioned it.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..prompts import ADJUDICATOR, CLINICAL_GUARDRAILS

logger = logging.getLogger(__name__)


@dataclass
class Verdict:
    """What OmniCare actually says. Possibly: 'I don't know, and here's why.'"""

    decision: str                       # converge | weigh | abstain
    conclusion: str
    clinical_term: str | None = None

    confidence: float = 0.0
    risk_score: float = 0.0
    risk_band: str = "low"

    disagreements: list[dict] = field(default_factory=list)
    reasoning_trail: list[str] = field(default_factory=list)

    abstained_because: str | None = None
    would_resolve_it: list[str] = field(default_factory=list)

    recommended_action: dict = field(default_factory=dict)
    organ: str | None = None

    human_signoff_required: bool = True
    red_flags: list[str] = field(default_factory=list)

    opinions: list[dict] = field(default_factory=list)

    @property
    def abstained(self) -> bool:
        return self.decision == "abstain"

    @property
    def is_emergency(self) -> bool:
        return self.risk_band == "emergency" or bool(self.red_flags)

    def to_dict(self) -> dict:
        return {
            "decision": self.decision,
            "conclusion": self.conclusion,
            "clinical_term": self.clinical_term,
            "confidence": round(self.confidence, 2),
            "risk_score": round(self.risk_score, 1),
            "risk_band": self.risk_band,
            "disagreements": self.disagreements,
            "reasoning_trail": self.reasoning_trail,
            "abstained": self.abstained,
            "abstained_because": self.abstained_because,
            "would_resolve_it": self.would_resolve_it,
            "recommended_action": self.recommended_action,
            "organ": self.organ,
            "human_signoff_required": self.human_signoff_required,
            "red_flags": self.red_flags,
            "deliberation": self.opinions,
        }


class Adjudicator:
    """
    Weighs the MDT. Allowed to refuse.

    There is a deterministic layer BEFORE the model runs. Some conditions must
    force an abstention regardless of what an LLM thinks — because the whole point
    of the safety property is that it does not depend on the model behaving.
    """

    def __init__(self, llm, core_system: str):
        self.llm = llm
        self.core_system = core_system

    def adjudicate(self, opinions: list[Any], context: str) -> Verdict:
        # ── Deterministic pre-checks ──────────────────────────────
        # These run first and can force an abstention on their own. A safety
        # property that relies on the model choosing to be safe is not a safety
        # property; it is a hope.
        forced = self._forced_abstention(opinions)
        if forced:
            logger.info("Deterministic abstention: %s", forced)
            return self._abstain(forced, opinions)

        # ── Model adjudication ────────────────────────────────────
        deliberation = self._render(opinions)

        try:
            raw = self.llm.generate_json(
                ADJUDICATOR.format(
                    core_system=self.core_system,
                    guardrails=CLINICAL_GUARDRAILS,
                    deliberation=deliberation,
                    context=context,
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Adjudicator failed")
            # If the adjudicator itself fails, that is the strongest possible
            # reason to abstain. It is not a reason to fall back on whichever
            # agent happened to be loudest.
            return self._abstain(
                "The reasoning system could not complete its review. "
                "This is not a diagnosis and should not be treated as one.",
                opinions,
                error=str(exc),
            )

        verdict = Verdict(
            decision=raw.get("decision", "abstain"),
            conclusion=raw.get("conclusion", ""),
            clinical_term=raw.get("clinical_term"),
            confidence=float(raw.get("confidence", 0.0)),
            risk_score=float(raw.get("risk_score", 0.0)),
            risk_band=raw.get("risk_band", "low"),
            disagreements=raw.get("disagreements", []),
            reasoning_trail=raw.get("reasoning_trail", []),
            abstained_because=raw.get("abstained_because"),
            would_resolve_it=raw.get("would_resolve_it", []),
            recommended_action=raw.get("recommended_action", {}),
            organ=raw.get("organ"),
            human_signoff_required=raw.get("human_signoff_required", True),
            red_flags=raw.get("red_flags", []),
            opinions=[o.to_dict() for o in opinions],
        )

        # ── Post-checks ───────────────────────────────────────────
        # The model is allowed to be wrong about its own safety. We are not.

        # A red flag overrides everything the model just said.
        if verdict.red_flags:
            verdict.risk_band = "emergency"
            verdict.risk_score = max(verdict.risk_score, 9.0)
            verdict.human_signoff_required = True

        # High risk always needs a human. No exceptions, no confidence threshold
        # that buys its way out.
        if verdict.risk_band in ("high", "emergency"):
            verdict.human_signoff_required = True

        return verdict

    # ── Deterministic safety layer ────────────────────────────────

    def _forced_abstention(self, opinions: list[Any]) -> str | None:
        """
        Conditions under which we abstain regardless of the model's view.

        Each of these is a case where a confident answer would be actively
        dangerous, and where we cannot trust a model to reliably notice that.
        """
        by_name = {o.agent: o for o in opinions}

        # 1. Allergy veto outstanding. Nothing proceeds over an allergy veto.
        records = by_name.get("records")
        if records and any("ALLERGY VETO" in c for c in records.concerns):
            veto = next(c for c in records.concerns if "ALLERGY VETO" in c)
            return (
                f"A medication conflict was flagged in your record — {veto}. "
                "A pharmacist or doctor needs to review this before anything is suggested."
            )

        # 2. The body contradicts the patient's account.
        bio = by_name.get("biometrics")
        if bio and any("CONTRADICTION" in c for c in bio.concerns):
            contradiction = next(c for c in bio.concerns if "CONTRADICTION" in c)
            return (
                f"Your wearable data does not match what you have described — {contradiction}. "
                "Until that is explained, any conclusion would be built on shaky ground."
            )

        # 3. Everyone is uncertain. Six weak opinions do not sum to one strong one.
        active = [o for o in opinions if not o.abstained]
        if active and all(o.is_weak for o in active):
            return (
                "Every part of the system is uncertain about this. "
                "Averaging six guesses does not produce an answer — it produces a guess "
                "with a decimal point. This needs a human."
            )

        # 4. Total system failure.
        if all(o.abstained for o in opinions):
            return (
                "No part of the system was able to form a view on this. "
                "That is a system limitation, not a reassurance about your symptoms."
            )

        return None

    def _abstain(self, reason: str, opinions: list[Any], error: str | None = None) -> Verdict:
        return Verdict(
            decision="abstain",
            conclusion=reason,
            confidence=0.0,
            risk_score=5.0,   # unknown is not low. Never default unknown to safe.
            risk_band="medium",
            abstained_because=reason,
            would_resolve_it=self._resolution_paths(opinions),
            recommended_action={
                "level": "gp",
                "timeframe": "48_hours",
                "what_to_do": "See a doctor. OmniCare cannot safely narrow this down.",
            },
            human_signoff_required=True,
            opinions=[o.to_dict() for o in opinions],
        )

    @staticmethod
    def _resolution_paths(opinions: list[Any]) -> list[str]:
        """What would actually settle this. Specific, actionable, cheap first."""
        paths: list[str] = []
        for o in opinions:
            for concern in o.concerns:
                if "CONTRADICTION" in concern:
                    paths.append("Take your temperature and log it.")
                if "ALLERGY VETO" in concern:
                    paths.append("Have a pharmacist review your allergy record.")
        if not paths:
            paths.append("A short consultation with a GP would resolve this quickly.")
        return list(dict.fromkeys(paths))  # dedupe, preserve order

    @staticmethod
    def _render(opinions: list[Any]) -> str:
        """
        Format the MDT for the adjudicating model.

        Abstentions are shown, not hidden. An agent choosing to say nothing is
        itself information — and if five agents abstain, the Adjudicator should
        see that rather than being handed one lonely confident opinion as though
        it were a consensus.
        """
        blocks: list[str] = []

        for o in opinions:
            if o.abstained:
                blocks.append(
                    f"[{o.agent.upper()}] — abstained. "
                    f"{o.error or 'No relevant contribution.'}"
                )
                continue

            lines = [
                f"[{o.agent.upper()}] (confidence {o.confidence:.2f})",
                f"  Position: {o.position}",
            ]
            if o.evidence:
                lines.append(f"  Reasoned from: {'; '.join(o.evidence)}")
            if o.concerns:
                lines.append(f"  Concerns: {'; '.join(o.concerns)}")
            if o.disagrees_with:
                lines.append(f"  Expects to disagree with: {', '.join(o.disagrees_with)}")

            # Speciality-specific detail the Adjudicator needs
            for key in (
                "differentials",
                "anomalies",
                "allergy_vetoes",
                "suggested",
                "contraindicated",
                "recommended_level",
                "relevant_signals",
                "differential_to_add",
            ):
                if o.payload.get(key):
                    lines.append(f"  {key}: {o.payload[key]}")

            blocks.append("\n".join(lines))

        return "\n\n".join(blocks)
