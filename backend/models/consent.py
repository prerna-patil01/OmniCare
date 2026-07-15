"""
The Consent Ledger.

This is the differentiator. Every other health app treats consent as a checkbox
you tick once at signup and never see again. Here it is a first-class object:
scoped, time-boxed, revocable, and auditable.

The DPDP Act 2023 is live in India. Every health startup is about to discover
that "I agree to the terms" is not consent. This model is what that looks like
when you take it seriously.
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum

from extensions import db


class ConsentScope(str, Enum):
    """WHAT can be seen. Field-level, not record-level."""

    MEDICAL_HISTORY = "medical_history"
    LIFESTYLE = "lifestyle"
    VITALS = "vitals"
    REPORTS = "reports"
    MENTAL_HEALTH = "mental_health"
    REPRODUCTIVE = "reproductive"
    GENETIC = "genetic"

    # Never gated. Withholding these can kill someone, and no consent
    # framework on earth requires that.
    ALLERGIES = "allergies"
    BLOOD_GROUP = "blood_group"


class ConsentPurpose(str, Enum):
    """WHY it can be seen. A grant for triage does not permit research."""

    TRIAGE = "triage"
    DOCTOR_SHARE = "doctor_share"
    HOSPITAL_ADMISSION = "hospital_admission"
    PHARMACY = "pharmacy"
    INSURANCE_CLAIM = "insurance_claim"
    POPULATION_RESEARCH = "population_research"
    EMERGENCY = "emergency"


class ConsentGrant(db.Model):
    __tablename__ = "consent_grants"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), index=True)

    scope = db.Column(db.String(40), index=True)
    purpose = db.Column(db.String(40), index=True)

    # WHO it was granted to. Null means OmniCare itself.
    grantee = db.Column(db.String(200))
    grantee_type = db.Column(db.String(30))  # omnicare|doctor|hospital|pharmacy|insurer

    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    revoked = db.Column(db.Boolean, default=False, index=True)
    revoked_at = db.Column(db.DateTime)
    revoked_reason = db.Column(db.String(300))

    # How many times this grant has actually been used. A grant nobody uses is
    # a grant that should probably be revoked, and showing the count makes that
    # visible to the patient.
    access_count = db.Column(db.Integer, default=0)
    last_accessed_at = db.Column(db.DateTime)

    @property
    def active(self):
        if self.revoked:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True

    @property
    def expires_in_days(self):
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)

    @classmethod
    def grant(cls, user_id, scope, purpose, grantee=None, grantee_type="omnicare", days=30):
        """
        Create a time-boxed grant.

        Default 30 days. Perpetual consent is not consent — it is surrender, and
        a patient who granted access in 2024 has not meaningfully agreed to
        anything happening in 2027.
        """
        return cls(
            user_id=user_id,
            scope=scope.value if isinstance(scope, Enum) else scope,
            purpose=purpose.value if isinstance(purpose, Enum) else purpose,
            grantee=grantee,
            grantee_type=grantee_type,
            expires_at=datetime.utcnow() + timedelta(days=days) if days else None,
        )

    def revoke(self, reason=None):
        self.revoked = True
        self.revoked_at = datetime.utcnow()
        self.revoked_reason = reason

    def touch(self):
        self.access_count = (self.access_count or 0) + 1
        self.last_accessed_at = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "scope": self.scope,
            "purpose": self.purpose,
            "grantee": self.grantee or "OmniCare",
            "grantee_type": self.grantee_type,
            "granted_at": self.granted_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "expires_in_days": self.expires_in_days,
            "active": self.active,
            "revoked": self.revoked,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "revoked_reason": self.revoked_reason,
            "access_count": self.access_count or 0,
            "last_accessed_at": self.last_accessed_at.isoformat()
            if self.last_accessed_at
            else None,
        }
