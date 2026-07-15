import uuid
from datetime import datetime

from extensions import db


class Ride(db.Model):
    """
    A ride is a deep link, not an API call.

    We store the destination and the generated links. No Uber/Ola API — partner
    approval takes months, and a deep link that opens the real app with the
    hospital pre-filled demos better than a JSON receipt anyway.
    """

    __tablename__ = "rides"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), index=True)

    destination = db.Column(db.String(200))
    dest_lat = db.Column(db.Float)
    dest_lng = db.Column(db.Float)

    provider = db.Column(db.String(20))     # uber | ola
    uber_deeplink = db.Column(db.Text)
    ola_deeplink = db.Column(db.Text)

    urgency = db.Column(db.String(20), default="scheduled")  # scheduled | emergency
    triage_id = db.Column(db.String(36), db.ForeignKey("triage_records.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "destination": self.destination,
            "dest_lat": self.dest_lat,
            "dest_lng": self.dest_lng,
            "provider": self.provider,
            "uber_deeplink": self.uber_deeplink,
            "ola_deeplink": self.ola_deeplink,
            "urgency": self.urgency,
            "created_at": self.created_at.isoformat(),
        }
