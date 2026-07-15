from extensions import db


class CareWorker(db.Model):
    """
    The moat.

    Nurses, ASHA workers, ANMs, physios. This is the last-mile physical layer
    that no other health app in India can dispatch — and it is the reason the
    AI is worth anything. An answer without a hand at the door is a search result.
    """

    __tablename__ = "care_workers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    role = db.Column(db.String(40), index=True)  # nurse|asha|anm|physio|caretaker|dietician

    experience_years = db.Column(db.Integer)
    rating = db.Column(db.Float)
    rate_inr_hour = db.Column(db.Integer)

    distance_km = db.Column(db.Float)
    available_from = db.Column(db.String(60))
    languages = db.Column(db.JSON, default=list)
    services = db.Column(db.JSON, default=list)

    verified = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "experience_years": self.experience_years,
            "rating": self.rating,
            "rate_inr_hour": self.rate_inr_hour,
            "distance_km": self.distance_km,
            "available_from": self.available_from,
            "languages": self.languages or [],
            "services": self.services or [],
            "verified": self.verified,
        }
