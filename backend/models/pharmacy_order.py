import uuid
from datetime import datetime

from extensions import db


class PharmacyOrder(db.Model):
    __tablename__ = "pharmacy_orders"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), index=True)

    items = db.Column(db.JSON, default=list)
    total_inr = db.Column(db.Float)
    status = db.Column(db.String(20), default="routed")   # routed|dispatched|delivered
    eta = db.Column(db.String(60))

    triage_id = db.Column(db.String(36), db.ForeignKey("triage_records.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "items": self.items or [],
            "total_inr": self.total_inr,
            "status": self.status,
            "eta": self.eta,
            "created_at": self.created_at.isoformat(),
        }
