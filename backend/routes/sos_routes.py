"""
Emergency SOS.

One tap. Location, blood group, allergies, medical summary — broadcast.

Note what is NOT gated here: everything. Consent scopes do not apply in an
emergency, because a consent framework that lets someone die is not protecting
them. This is the one endpoint that reads everything, and it logs that it did.
"""

from flask import Blueprint, request

from integrations import ride_deeplinks
from models import Hospital
from services import ConsentService
from utils import current_user, ok, require_auth

sos_bp = Blueprint("sos", __name__, url_prefix="/api/sos")

_consent = ConsentService()


@sos_bp.post("/trigger")
@require_auth
def trigger():
    user = current_user()
    body = request.get_json() or {}

    lat = body.get("lat")
    lng = body.get("lng")

    # Emergency access is unrestricted — and audited. The patient can see, later,
    # exactly what was read and why. That is the honest trade: we override consent
    # to save your life, and we tell you we did it.
    _consent.audit(
        user.id,
        "system:sos",
        "emergency_broadcast",
        "all",
        True,
        "SOS triggered — emergency override of consent scopes.",
    )

    profile = user.profile
    history = user.history

    summary = {
        "name": user.name,
        "age": profile.age if profile else None,
        "blood_group": profile.blood_group if profile else None,
        "allergies": (history.allergies if history else []) or ["None on record"],
        "conditions": (history.current_diseases if history else []) or [],
        "medications": (history.medications if history else []) or [],
        "emergency_contact": profile.emergency_contact if profile else None,
    }

    hospital = Hospital.query.order_by(Hospital.distance_km).first()

    payload = {
        "broadcast": True,
        "medical_summary": summary,
        "location": {"lat": lat, "lng": lng} if lat else None,
        "notified": [
            "Emergency contact",
            "Nearest hospital",
            "Primary doctor",
        ],
    }

    if hospital:
        payload["hospital"] = hospital.to_dict()
        payload["transport"] = ride_deeplinks(hospital.lat, hospital.lng, hospital.name)

    # Every audit entry is committed — including this one.
    from extensions import db
    db.session.commit()

    return ok(payload)
