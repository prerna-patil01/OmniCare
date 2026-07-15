from datetime import datetime

from extensions import db


class VitalReading(db.Model):
    """
    One wearable sample.

    Time-series, append-only. We never update a reading — a heart rate that was
    72 at 3pm was 72 at 3pm, regardless of what the watch says later.
    """

    __tablename__ = "vital_readings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), index=True)

    heart_rate = db.Column(db.Float)
    hrv = db.Column(db.Float)
    spo2 = db.Column(db.Float)
    sleep_hours = db.Column(db.Float)
    steps = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    bp_systolic = db.Column(db.Integer)
    bp_diastolic = db.Column(db.Integer)

    source = db.Column(db.String(40), default="apple_health")
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "heart_rate": self.heart_rate,
            "hrv": self.hrv,
            "spo2": self.spo2,
            "sleep_hours": self.sleep_hours,
            "steps": self.steps,
            "temperature": self.temperature,
            "bp": f"{self.bp_systolic}/{self.bp_diastolic}"
            if self.bp_systolic
            else None,
            "source": self.source,
            "recorded_at": self.recorded_at.isoformat(),
        }
