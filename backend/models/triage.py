import uuid
from datetime import datetime

from extensions import db


class TriageRecord(db.Model):
    """
    One complete deliberation. Prediction AND, eventually, ground truth.

    The `actual_*` columns are what make calibration possible. Most systems
    never fill them in, which is why most systems never learn they were wrong.
    """

    __tablename__ = "triage_records"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), index=True)
    conversation_id = db.Column(db.String(36), db.ForeignKey("conversations.id"))

    # ── What Omni said ────────────────────────────────────────────
    decision = db.Column(db.String(20))          # converge | weigh | abstain
    conclusion = db.Column(db.Text)
    clinical_term = db.Column(db.String(200))
    condition = db.Column(db.String(200), index=True)  # for population aggregation

    confidence = db.Column(db.Float)
    risk_score = db.Column(db.Float)
    risk_band = db.Column(db.String(20))

    abstained = db.Column(db.Boolean, default=False)
    abstained_because = db.Column(db.Text)
    would_resolve_it = db.Column(db.JSON, default=list)

    # ── The deliberation, preserved ───────────────────────────────
    deliberation = db.Column(db.JSON, default=list)   # every agent opinion
    disagreements = db.Column(db.JSON, default=list)
    reasoning_trail = db.Column(db.JSON, default=list)
    consent_blocks = db.Column(db.JSON, default=list)

    recommended_action = db.Column(db.JSON, default=dict)
    red_flags = db.Column(db.JSON, default=list)
    organ = db.Column(db.String(30))

    human_signoff_required = db.Column(db.Boolean, default=True)
    signed_off_by = db.Column(db.String(120))
    signed_off_at = db.Column(db.DateTime)

    # ── What actually happened ────────────────────────────────────
    actual_condition = db.Column(db.String(200))
    actual_severity = db.Column(db.String(20))
    confirmed_by = db.Column(db.String(120))
    confirmed_at = db.Column(db.DateTime)
    correct = db.Column(db.Boolean)

    region = db.Column(db.String(120), index=True)
    elapsed_ms = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    @property
    def resolved(self):
        return self.actual_condition is not None

    def to_dict(self):
        return {
            "id": self.id,
            "decision": self.decision,
            "conclusion": self.conclusion,
            "clinical_term": self.clinical_term,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "risk_band": self.risk_band,
            "abstained": self.abstained,
            "abstained_because": self.abstained_because,
            "would_resolve_it": self.would_resolve_it or [],
            "deliberation": self.deliberation or [],
            "disagreements": self.disagreements or [],
            "reasoning_trail": self.reasoning_trail or [],
            "consent_blocks": self.consent_blocks or [],
            "recommended_action": self.recommended_action or {},
            "red_flags": self.red_flags or [],
            "organ": self.organ,
            "human_signoff_required": self.human_signoff_required,
            "resolved": self.resolved,
            "actual_condition": self.actual_condition,
            "correct": self.correct,
            "elapsed_ms": self.elapsed_ms,
            "created_at": self.created_at.isoformat(),
        }
