import uuid
from datetime import datetime

from extensions import db


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"))

    mode = db.Column(db.String(20))     # video | in_person | home_visit
    slot = db.Column(db.String(60))
    status = db.Column(db.String(20), default="confirmed")

    triage_id = db.Column(db.String(36), db.ForeignKey("triage_records.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship("Doctor", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "mode": self.mode,
            "slot": self.slot,
            "status": self.status,
            "doctor": self.doctor.to_dict() if self.doctor else None,
            "created_at": self.created_at.isoformat(),
        }
