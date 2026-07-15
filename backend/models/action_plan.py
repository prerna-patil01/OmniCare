"""
An autonomous action plan.

This is where "the AI acts" lives — and where it is kept honest. The agent plans
and STAGES a complete bundle of actions (find the doctor, hold the slot, build the
cart, match the nurse) entirely on its own. Every step runs to the edge of the
irreversible commit, and then stops.

One tap commits the bundle. To the patient it feels fully autonomous — the work is
done, the ride is queued, the meds are in the cart. But the single action with
consequences stays human. That is not a limitation bolted on; it is the product's
whole safety thesis expressed as one column: `committed_at`.
"""

import uuid
from datetime import datetime

from extensions import db


class ActionPlan(db.Model):
    __tablename__ = "action_plans"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), index=True)
    triage_id = db.Column(db.String(36), db.ForeignKey("triage_records.id"))

    # ── The plan ──────────────────────────────────────────────────
    goal = db.Column(db.String(300))            # "Get you seen for the gallbladder pain"
    steps = db.Column(db.JSON, default=list)     # everything the agent staged
    # each step: {type, description, status, payload, reversible, cost_inr}

    reasoning = db.Column(db.Text)               # why the agent chose this bundle
    total_cost_inr = db.Column(db.Integer)

    # ── State machine ─────────────────────────────────────────────
    # staged → (human taps) → committed → executed
    #        → (human declines) → dismissed
    status = db.Column(db.String(20), default="staged", index=True)

    staged_at = db.Column(db.DateTime, default=datetime.utcnow)
    committed_at = db.Column(db.DateTime)        # ← the one human moment
    committed_by = db.Column(db.String(120))
    executed_at = db.Column(db.DateTime)

    execution_result = db.Column(db.JSON, default=dict)

    @property
    def is_committed(self):
        return self.committed_at is not None

    @property
    def reversible_steps(self):
        return [s for s in (self.steps or []) if s.get("reversible")]

    @property
    def irreversible_steps(self):
        """The steps that are WHY a human taps. Purchases, bookings, dispatches."""
        return [s for s in (self.steps or []) if not s.get("reversible")]

    def to_dict(self):
        return {
            "id": self.id,
            "goal": self.goal,
            "steps": self.steps or [],
            "reasoning": self.reasoning,
            "total_cost_inr": self.total_cost_inr,
            "status": self.status,
            "reversible_count": len(self.reversible_steps),
            "irreversible_count": len(self.irreversible_steps),
            "staged_at": self.staged_at.isoformat() if self.staged_at else None,
            "committed_at": self.committed_at.isoformat() if self.committed_at else None,
            "committed_by": self.committed_by,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "execution_result": self.execution_result or {},
        }
