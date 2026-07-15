"""
The Digital Twin.

This is the spine of OmniCare. Not a page, not a feature — the object that holds
the patient's whole state and projects it forward.

A health app tells you what your heart rate IS. A digital twin tells you where
your heart rate is GOING, given who you are: your mother's gallstones, your
chronically low hydration, your resting HR that has climbed 6% in a fortnight.
It is the difference between a mirror and a weather forecast.

The twin is computed, never hand-entered. Every field is derived from data the
patient already gave us — vitals, history, lifestyle, reports, and the calibrated
accuracy of Omni's past predictions. It is the patient, modelled.
"""

import uuid
from datetime import datetime

from extensions import db


class DigitalTwin(db.Model):
    """
    A materialised snapshot of the patient's modelled state.

    Recomputed on demand (and cached). We store snapshots rather than computing
    live every time because the projection is expensive — six-factor risk
    synthesis across the whole record — and because a stored history of twins
    lets us show DRIFT: "your cardiovascular risk was 3.1 last month, it is 3.8
    now." Trajectory is the product.
    """

    __tablename__ = "digital_twins"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), index=True)

    # ── Overall state ─────────────────────────────────────────────
    health_score = db.Column(db.Float)          # 0-100, composite
    biological_age = db.Column(db.Float)         # vs chronological
    chronological_age = db.Column(db.Integer)
    trajectory = db.Column(db.String(20))        # improving | stable | declining

    # ── System-level risk (the body, by domain) ──────────────────
    # Each 0-10. This is what colours the twin's body map.
    system_risk = db.Column(db.JSON, default=dict)
    # e.g. {"cardiovascular": 3.8, "metabolic": 5.1, "hepatic": 4.2, ...}

    # ── What the patient is PRONE to ──────────────────────────────
    # The forward projection. Ranked, with the reasoning and the lever.
    predispositions = db.Column(db.JSON, default=list)
    # [{condition, risk_level, horizon, drivers[], modifiable[], confidence}]

    # ── What is trending, right now ───────────────────────────────
    active_signals = db.Column(db.JSON, default=list)
    # [{signal, direction, magnitude, interpretation, severity}]

    # ── What would change the trajectory ──────────────────────────
    interventions = db.Column(db.JSON, default=list)
    # [{action, targets[], projected_effect, effort}]

    # ── Provenance ────────────────────────────────────────────────
    computed_from = db.Column(db.JSON, default=dict)  # what data fed this twin
    confidence = db.Column(db.Float)                  # how complete the record was
    narrative = db.Column(db.Text)                    # the plain-language summary

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "health_score": self.health_score,
            "biological_age": self.biological_age,
            "chronological_age": self.chronological_age,
            "age_gap": (
                round(self.biological_age - self.chronological_age, 1)
                if self.biological_age and self.chronological_age
                else None
            ),
            "trajectory": self.trajectory,
            "system_risk": self.system_risk or {},
            "predispositions": self.predispositions or [],
            "active_signals": self.active_signals or [],
            "interventions": self.interventions or [],
            "computed_from": self.computed_from or {},
            "confidence": self.confidence,
            "narrative": self.narrative,
            "created_at": self.created_at.isoformat(),
        }
