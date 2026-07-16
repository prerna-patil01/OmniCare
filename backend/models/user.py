import uuid
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), unique=True, index=True)
    phone = db.Column(db.String(20), unique=True, index=True)
    password_hash = db.Column(db.String(255))

    # ABHA — the national health ID. Stored, never sent to a model.
    abha_id = db.Column(db.String(20), unique=True, index=True)

    auth_provider = db.Column(db.String(20), default="email")  # email|google|phone|abha
    region = db.Column(db.String(120), default="Artist Village")

    onboarded = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship("HealthProfile", uselist=False, backref="user", lazy="joined")
    history = db.relationship("MedicalHistory", uselist=False, backref="user", lazy="joined")
    lifestyle = db.relationship("Lifestyle", uselist=False, backref="user", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "abha_id": self._mask_abha(),
            "region": self.region,
            "onboarded": self.onboarded,
        }

    def _mask_abha(self):
        """Never return a full ABHA to the client. Last four is enough to recognise."""
        if not self.abha_id:
            return None
        return f"····{self.abha_id[-4:]}"

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        return bool(self.password_hash and check_password_hash(self.password_hash, password))
