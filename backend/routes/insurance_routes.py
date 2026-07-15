"""
Insurance. Architected, not integrated.

Real integration needs IRDAI-approved insurer APIs and weeks of onboarding. The
rails are here — stored policy, cashless-eligibility check against the hospital
directory — the live insurer handshake is not. Honest scope for a hackathon.
"""

from flask import Blueprint, request

from extensions import db
from models import Hospital, InsurancePolicy
from utils import current_user, ok, error, require_auth

insurance_bp = Blueprint("insurance", __name__, url_prefix="/api/insurance")


@insurance_bp.get("")
@require_auth
def policies():
    user = current_user()
    items = InsurancePolicy.query.filter_by(user_id=user.id).all()
    return ok([p.to_dict() for p in items])


@insurance_bp.post("/link")
@require_auth
def link():
    user = current_user()
    body = request.get_json() or {}

    policy = InsurancePolicy(
        user_id=user.id,
        provider=body.get("provider"),
        policy_number=body.get("policy_number"),
        policy_type=body.get("policy_type", "individual"),
        sum_insured_inr=int(body.get("sum_insured_inr", 500000)),
        valid_till=body.get("valid_till"),
        cashless=bool(body.get("cashless", True)),
    )
    db.session.add(policy)
    db.session.commit()
    return ok(policy.to_dict(), status=201)


@insurance_bp.get("/cashless-hospitals")
@require_auth
def cashless_hospitals():
    """Which nearby hospitals accept cashless claims. Reads the seeded directory."""
    items = Hospital.query.filter_by(cashless=True).order_by(Hospital.distance_km).all()
    return ok([h.to_dict() for h in items])
