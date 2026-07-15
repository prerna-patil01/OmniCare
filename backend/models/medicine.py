from extensions import db


class Medicine(db.Model):
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), index=True)
    generic = db.Column(db.String(160))
    form = db.Column(db.String(40))
    strength = db.Column(db.String(40))

    price_inr = db.Column(db.Float)
    prescription_required = db.Column(db.Boolean, default=False)
    in_stock = db.Column(db.Boolean, default=True)
    delivery_eta = db.Column(db.String(60))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "generic": self.generic,
            "form": self.form,
            "strength": self.strength,
            "price_inr": self.price_inr,
            "prescription_required": self.prescription_required,
            "in_stock": self.in_stock,
            "delivery_eta": self.delivery_eta,
        }
