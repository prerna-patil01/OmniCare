from datetime import datetime

from extensions import db


class HealthProfile(db.Model):
    __tablename__ = "health_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), unique=True)

    dob = db.Column(db.Date)
    gender = db.Column(db.String(30))
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    blood_group = db.Column(db.String(10))
    emergency_contact = db.Column(db.String(20))

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def bmi(self):
        """Derived, never stored. A stored BMI goes stale the moment weight changes."""
        if not self.height_cm or not self.weight_kg or self.height_cm < 50:
            return None
        return round(self.weight_kg / ((self.height_cm / 100) ** 2), 1)

    @property
    def age(self):
        if not self.dob:
            return None
        today = datetime.utcnow().date()
        return today.year - self.dob.year - (
            (today.month, today.day) < (self.dob.month, self.dob.day)
        )

    def to_dict(self):
        return {
            "dob": self.dob.isoformat() if self.dob else None,
            "age": self.age,
            "gender": self.gender,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "bmi": self.bmi,
            "blood_group": self.blood_group,
            "emergency_contact": self.emergency_contact,
        }
