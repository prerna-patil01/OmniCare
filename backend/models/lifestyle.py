from datetime import datetime

from extensions import db


class Lifestyle(db.Model):
    __tablename__ = "lifestyles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), unique=True)

    smoking = db.Column(db.String(30))
    alcohol = db.Column(db.String(30))
    food_habits = db.Column(db.String(40))
    exercise = db.Column(db.String(40))
    stress = db.Column(db.String(30))
    sleep = db.Column(db.String(20))
    hydration_l = db.Column(db.Float)
    occupation = db.Column(db.String(120))

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "smoking": self.smoking,
            "alcohol": self.alcohol,
            "food_habits": self.food_habits,
            "exercise": self.exercise,
            "stress": self.stress,
            "sleep": self.sleep,
            "hydration_l": self.hydration_l,
            "occupation": self.occupation,
        }
