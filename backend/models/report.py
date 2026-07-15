import uuid
from datetime import datetime

from extensions import db


class Report(db.Model):
    """An uploaded document, plus what the vision model extracted from it."""

    __tablename__ = "reports"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), index=True)

    filename = db.Column(db.String(300))
    stored_path = db.Column(db.String(500))
    document_type = db.Column(db.String(40))
    report_date = db.Column(db.String(20))
    lab_name = db.Column(db.String(200))

    biomarkers = db.Column(db.JSON, default=list)
    medications = db.Column(db.JSON, default=list)
    impressions = db.Column(db.JSON, default=list)

    abnormal_summary = db.Column(db.Text)
    unreadable_sections = db.Column(db.JSON, default=list)
    has_ambiguous_medication = db.Column(db.Boolean, default=False)
    confidence = db.Column(db.Float, default=0.0)

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def abnormal(self):
        return [
            b
            for b in (self.biomarkers or [])
            if b.get("flag") in ("high", "low", "critical")
        ]

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "document_type": self.document_type,
            "report_date": self.report_date,
            "lab_name": self.lab_name,
            "biomarkers": self.biomarkers or [],
            "medications": self.medications or [],
            "impressions": self.impressions or [],
            "abnormal_summary": self.abnormal_summary,
            "abnormal_count": len(self.abnormal),
            "has_ambiguous_medication": self.has_ambiguous_medication,
            "unreadable_sections": self.unreadable_sections or [],
            "confidence": self.confidence,
            "uploaded_at": self.uploaded_at.isoformat(),
        }
