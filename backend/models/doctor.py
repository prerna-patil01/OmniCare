from extensions import db


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    specialty = db.Column(db.String(80), index=True)
    qualification = db.Column(db.String(120))
    hospital = db.Column(db.String(200))

    experience_years = db.Column(db.Integer)
    rating = db.Column(db.Float)
    review_count = db.Column(db.Integer)
    fee_inr = db.Column(db.Integer)

    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    distance_km = db.Column(db.Float)

    video_available = db.Column(db.Boolean, default=True)
    next_slot = db.Column(db.String(60))
    languages = db.Column(db.JSON, default=list)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "specialty": self.specialty,
            "qualification": self.qualification,
            "hospital": self.hospital,
            "experience_years": self.experience_years,
            "rating": self.rating,
            "review_count": self.review_count,
            "fee_inr": self.fee_inr,
            "distance_km": self.distance_km,
            "video_available": self.video_available,
            "next_slot": self.next_slot,
            "languages": self.languages or [],
            "lat": self.lat,
            "lng": self.lng,
        }


class Hospital(db.Model):
    """Lives here alongside Doctor — both are 'where care happens' directory rows."""

    __tablename__ = "hospitals"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    distance_km = db.Column(db.Float)

    er_load_pct = db.Column(db.Integer)
    cashless = db.Column(db.Boolean, default=True)
    specialties = db.Column(db.JSON, default=list)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "lat": self.lat,
            "lng": self.lng,
            "distance_km": self.distance_km,
            "er_load_pct": self.er_load_pct,
            "cashless": self.cashless,
            "specialties": self.specialties or [],
        }
