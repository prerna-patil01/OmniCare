import uuid
from datetime import datetime

from extensions import db


class CareBooking(db.Model):
    __tablename__ = "care_bookings"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), index=True)
    worker_id = db.Column(db.Integer, db.ForeignKey("care_workers.id"))

    hours = db.Column(db.Integer, default=1)
    starts_at = db.Column(db.String(60))
    total_inr = db.Column(db.Integer)
    status = db.Column(db.String(20), default="confirmed")

    triage_id = db.Column(db.String(36), db.ForeignKey("triage_records.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    worker = db.relationship("CareWorker", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "hours": self.hours,
            "starts_at": self.starts_at,
            "total_inr": self.total_inr,
            "status": self.status,
            "worker": self.worker.to_dict() if self.worker else None,
            "created_at": self.created_at.isoformat(),
        }
