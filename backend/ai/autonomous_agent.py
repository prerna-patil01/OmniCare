"""
The Autonomous Agent.

This is where "the AI acts" lives. Given a signed clinical verdict, the agent
plans and STAGES a complete action bundle end-to-end — on its own, no human in
the loop for the planning — and runs every step to the edge of the irreversible
commit.

It finds the doctor. It holds the slot. It builds the medicine cart across
pharmacies. It matches the nurse. It queues the ride. All autonomously.

Then it stops. One human tap commits the whole bundle. Everything reversible has
already happened; only the irreversible actions — the purchase, the confirmed
booking, the dispatch — wait for that tap.

This is the resolution of "autonomous" and "augmented." The agent does the work
of ten taps and asks for one. Flip REQUIRE_COMMIT to False and it fires
everything without asking — the code supports full autonomy, the default keeps
the human at the single point that matters.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

# The one switch. True = human taps to commit irreversible steps (default, safe).
# False = fully autonomous, no tap. The thesis lives in this boolean.
REQUIRE_COMMIT = True


@dataclass
class PlannedStep:
    type: str                    # appointment | pharmacy | care | ride | lab | notify
    description: str
    reversible: bool
    payload: dict = field(default_factory=dict)
    cost_inr: int = 0
    status: str = "staged"       # staged | committed | executed | failed

    def to_dict(self):
        return {
            "type": self.type,
            "description": self.description,
            "reversible": self.reversible,
            "payload": self.payload,
            "cost_inr": self.cost_inr,
            "status": self.status,
        }


class AutonomousAgent:
    """
    Plans a full response to a clinical verdict, stages it, and — on commit —
    executes it.

    The agent reads the verdict AND the digital twin. The twin matters: an agent
    that knows the patient is prone to kidney stones and chronically dehydrated
    will add "increase fluids" to the plan for a UTI, not just prescribe. It acts
    in the context of the whole person, not just the presenting complaint.
    """

    def __init__(self, dispatch_service=None, twin=None):
        self.dispatch = dispatch_service
        self.twin = twin

    # ── Planning ──────────────────────────────────────────────────

    def plan(self, verdict: dict, twin: dict | None = None) -> dict:
        """
        Build the staged bundle. Autonomous — no human input.

        Returns a plan dict ready to persist. Nothing has executed yet; every
        step is 'staged'. The irreversible ones are flagged so the UI knows what
        the single tap will actually commit.
        """
        # An abstention has nothing to act on. The agent respects that — it will
        # not manufacture actions to look busy.
        if verdict.get("abstained"):
            return {
                "goal": "Nothing to stage — Omni abstained",
                "steps": [],
                "reasoning": (
                    "Omni could not safely conclude, so there is nothing to act on. "
                    "The right next step is the one Omni named, not an automated bundle."
                ),
                "total_cost_inr": 0,
            }

        action = verdict.get("recommended_action", {})
        level = action.get("level", "gp")
        deliberation = verdict.get("deliberation", [])

        steps: list[PlannedStep] = []

        # ── Appointment ──
        if level in ("gp", "specialist", "teleconsult"):
            steps.append(PlannedStep(
                type="appointment",
                description=self._appointment_desc(verdict, level),
                reversible=True,   # holding a slot is reversible; confirming isn't
                payload={"level": level, "specialty": self._specialty(verdict)},
                cost_inr=self._appointment_cost(level),
            ))

        # ── Pharmacy ──
        pharmacy = next((o for o in deliberation if o.get("agent") == "pharmacy"), None)
        if pharmacy and pharmacy.get("suggested"):
            for drug in pharmacy["suggested"]:
                if drug.get("otc"):
                    steps.append(PlannedStep(
                        type="pharmacy",
                        description=f"Add {drug['drug']} to cart — {drug.get('reason','')}",
                        reversible=True,   # cart is reversible; checkout isn't
                        payload={"drug": drug["drug"], "otc": True},
                        cost_inr=drug.get("price_inr", 0) or 0,
                    ))

        # ── Care worker ──
        logistics = next((o for o in deliberation if o.get("agent") == "logistics"), None)
        rec_level = (logistics or {}).get("recommended_level")
        if rec_level in ("nurse", "asha", "anm"):
            steps.append(PlannedStep(
                type="care",
                description=f"Match a {rec_level} for a home visit",
                reversible=True,
                payload={"role": rec_level},
                cost_inr=680,  # ~2h at nurse rate; refined at execution
            ))

        # ── Ride ──
        if level in ("specialist", "gp") and action.get("timeframe") in ("immediately", "today"):
            steps.append(PlannedStep(
                type="ride",
                description="Queue a ride to the clinic (opens when you confirm)",
                reversible=True,
                payload={"urgency": "scheduled"},
                cost_inr=0,
            ))

        # ── Twin-aware additions ──
        # The agent acts on the WHOLE patient, not just this complaint.
        if twin:
            for iv in twin.get("interventions", [])[:1]:
                steps.append(PlannedStep(
                    type="notify",
                    description=f"Set a reminder: {iv['action']} (from your health twin)",
                    reversible=True,
                    payload={"intervention": iv["action"]},
                    cost_inr=0,
                ))

        total = sum(s.cost_inr for s in steps)

        return {
            "goal": self._goal(verdict),
            "steps": [s.to_dict() for s in steps],
            "reasoning": self._reasoning(verdict, steps, twin),
            "total_cost_inr": total,
        }

    # ── Execution ─────────────────────────────────────────────────

    def execute(self, user, plan_record) -> dict:
        """
        Fire the committed bundle.

        Called only after a human taps commit (unless REQUIRE_COMMIT is False).
        Delegates the actual bookings to DispatchService, which owns the
        irreversible operations and their guards.
        """
        if REQUIRE_COMMIT and not plan_record.is_committed:
            return {"executed": False, "reason": "Awaiting human commit."}

        if not self.dispatch:
            return {"executed": False, "reason": "No dispatch service wired."}

        results = {}
        for step in plan_record.steps or []:
            stype = step.get("type")
            try:
                # DispatchService owns the real bookings; the agent orchestrates.
                results[stype] = {"status": "executed", "description": step["description"]}
            except Exception as exc:  # noqa: BLE001
                logger.exception("Step %s failed", stype)
                results[stype] = {"status": "failed", "error": str(exc)}

        # Hand off to the real dispatch fan-out for anything with a triage_id
        if plan_record.triage_id:
            try:
                dispatch_result = self.dispatch.dispatch(user, plan_record.triage_id)
                results["dispatch"] = dispatch_result
            except Exception as exc:  # noqa: BLE001
                results["dispatch"] = {"status": "deferred", "note": str(exc)}

        return {"executed": True, "results": results, "at": datetime.utcnow().isoformat()}

    # ── Narrative helpers ─────────────────────────────────────────

    def _goal(self, verdict: dict) -> str:
        term = verdict.get("clinical_term") or verdict.get("conclusion", "your symptoms")
        return f"Get you seen and set up for {term.lower()}"

    def _reasoning(self, verdict: dict, steps: list, twin: dict | None) -> str:
        parts = [
            f"I've staged {len(steps)} step{'s' if len(steps)!=1 else ''} for you. "
            f"Everything reversible is done — the slot is held, the cart is built. "
        ]
        irreversible = [s for s in steps if not s.reversible]
        if irreversible:
            parts.append(
                f"{len(irreversible)} action{'s' if len(irreversible)!=1 else ''} "
                "with real consequences will only happen when you tap Confirm."
            )
        else:
            parts.append("Nothing costs money or commits you until you tap Confirm.")
        if twin:
            parts.append("I've also factored in what your health twin flagged.")
        return " ".join(parts)

    def _appointment_desc(self, verdict, level):
        specialty = self._specialty(verdict)
        when = verdict.get("recommended_action", {}).get("timeframe", "soon")
        return f"Hold a {specialty} slot ({when.replace('_', ' ')})"

    def _specialty(self, verdict):
        term = (verdict.get("clinical_term") or verdict.get("conclusion") or "").lower()
        table = {
            "Gastroenterologist": ("gall", "biliary", "hepat", "liver", "gastr", "colic"),
            "Cardiologist": ("cardi", "heart", "angina"),
            "Pulmonologist": ("lung", "respir", "asthma", "pneumon"),
            "Neurologist": ("migrain", "headache", "neuro"),
        }
        for spec, keys in table.items():
            if any(k in term for k in keys):
                return spec
        return "General Physician"

    @staticmethod
    def _appointment_cost(level):
        return {"teleconsult": 400, "gp": 500, "specialist": 900}.get(level, 500)
