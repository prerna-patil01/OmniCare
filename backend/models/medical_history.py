from datetime import datetime

from extensions import db


class MedicalHistory(db.Model):
    """
    Free-form clinical history.

    Stored as JSON lists rather than normalised tables. Real medical histories
    do not fit an enum — "Dengue (2021), suspected" is a legitimate entry, and
    forcing it into a foreign key loses the "suspected."
    """

    __tablename__ = "medical_histories"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), unique=True)

    allergies = db.Column(db.JSON, default=list)
    current_diseases = db.Column(db.JSON, default=list)
    past_diseases = db.Column(db.JSON, default=list)
    surgeries = db.Column(db.JSON, default=list)
    medications = db.Column(db.JSON, default=list)
    family_history = db.Column(db.JSON, default=list)
    vaccinations = db.Column(db.JSON, default=list)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "allergies": self.allergies or [],
            "current_diseases": self.current_diseases or [],
            "past_diseases": self.past_diseases or [],
            "surgeries": self.surgeries or [],
            "medications": self.medications or [],
            "family_history": self.family_history or [],
            "vaccinations": self.vaccinations or [],
        }
