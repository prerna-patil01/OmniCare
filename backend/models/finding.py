import uuid
from datetime import datetime

from extensions import db


class Finding(db.Model):
    """
    A clinical finding — an abnormal result or a triage conclusion.

    The anatomy PAGE is gone (removed per the product decision), but findings are
    still produced by report extraction and triage. They surface in the Digital
    Twin's active signals and on the dashboard, just not on a body diagram.
    """

    __tablename__ = "findings"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), index=True)

    organ = db.Column(db.String(30), index=True)   # retained for grouping, not rendered on a body
    conclusion = db.Column(db.Text)
    clinical_term = db.Column(db.String(200))
    annotation = db.Column(db.String(80))

    severity = db.Column(db.String(20))
    risk_score = db.Column(db.Float)

    source = db.Column(db.String(30))
    source_id = db.Column(db.String(36))

    active = db.Column(db.Boolean, default=True)
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "organ": self.organ,
            "conclusion": self.conclusion,
            "clinical_term": self.clinical_term,
            "annotation": self.annotation,
            "severity": self.severity,
            "risk_score": self.risk_score,
            "source": self.source,
            "active": self.active,
            "created_at": self.created_at.isoformat(),
        }
