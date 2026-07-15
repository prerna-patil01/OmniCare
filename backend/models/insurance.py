import uuid
from datetime import datetime

from extensions import db


class InsurancePolicy(db.Model):
    """
    Insurance. Architected, not integrated.

    Real integration means IRDAI-approved insurer APIs and weeks of onboarding.
    For the demo this is a stored policy the user can see, plus a cashless-eligibility
    check that reads the seeded hospital directory. Honest scope: the rails are
    here, the live insurer handshake is not.
    """

    __tablename__ = "insurance_policies"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), index=True)

    provider = db.Column(db.String(120))
    policy_number = db.Column(db.String(60))
    policy_type = db.Column(db.String(60))       # individual | family_floater | group
    sum_insured_inr = db.Column(db.Integer)
    used_inr = db.Column(db.Integer, default=0)

    valid_till = db.Column(db.String(20))
    cashless = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def available_inr(self):
        return (self.sum_insured_inr or 0) - (self.used_inr or 0)

    def to_dict(self):
        return {
            "id": self.id,
            "provider": self.provider,
            "policy_number": self._mask(),
            "policy_type": self.policy_type,
            "sum_insured_inr": self.sum_insured_inr,
            "used_inr": self.used_inr,
            "available_inr": self.available_inr,
            "valid_till": self.valid_till,
            "cashless": self.cashless,
        }

    def _mask(self):
        if not self.policy_number:
            return None
        return f"····{self.policy_number[-4:]}"
