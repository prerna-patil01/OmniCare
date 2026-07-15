"""
Care workers — the moat.

Nurses, ASHA workers, ANMs, physios. No other health app in India can dispatch
these, and an AI answer without a hand at the door is just a search result.
"""

from flask import Blueprint, request

from extensions import db
from models import CareBooking, CareWorker
from utils import current_user, ok, error, require_auth

care_bp = Blueprint("care", __name__, url_prefix="/api/care")


@care_bp.get("/workers")
def workers():
    q = CareWorker.query

    role = request.args.get("role")
    if role:
        q = q.filter_by(role=role)

    max_rate = request.args.get("max_rate", type=int)
    if max_rate:
        q = q.filter(CareWorker.rate_inr_hour <= max_rate)

    items = q.order_by(CareWorker.distance_km).all()

    by_role = {}
    for w in items:
        by_role.setdefault(w.role, []).append(w.to_dict())

    return ok({"workers": [w.to_dict() for w in items], "by_role": by_role})


@care_bp.post("/book")
@require_auth
def book():
    user = current_user()
    body = request.get_json() or {}

    worker = CareWorker.query.get(body.get("worker_id"))
    if not worker:
        return error("No such care worker.", 404)

    hours = int(body.get("hours", 2))

    booking = CareBooking(
        user_id=user.id,
        worker_id=worker.id,
        hours=hours,
        starts_at=body.get("starts_at", worker.available_from),
        total_inr=(worker.rate_inr_hour or 0) * hours,
        status="confirmed",
        triage_id=body.get("triage_id"),
    )
    db.session.add(booking)
    db.session.commit()

    return ok(booking.to_dict(), status=201)


@care_bp.get("/bookings")
@require_auth
def bookings():
    user = current_user()
    items = (
        CareBooking.query.filter_by(user_id=user.id)
        .order_by(CareBooking.created_at.desc())
        .all()
    )
    return ok([b.to_dict() for b in items])


# ── Home sample collection ────────────────────────────────────────

@care_bp.post("/sample-collection")
@require_auth
def sample_collection():
    """
    Book a phlebotomist for at-home blood/sample collection.

    A lab_technician CareWorker with a time slot. This is the 'home sample
    collection' item — a real booking against the care directory.
    """
    user = current_user()
    body = request.get_json() or {}

    worker = (
        CareWorker.query.filter_by(role="lab_technician")
        .order_by(CareWorker.distance_km)
        .first()
    )
    if not worker:
        return error("No lab technician available right now.", 404)

    booking = CareBooking(
        user_id=user.id,
        worker_id=worker.id,
        hours=1,
        starts_at=body.get("slot", worker.available_from),
        total_inr=worker.rate_inr_hour or 250,
        status="confirmed",
        triage_id=body.get("triage_id"),
    )
    db.session.add(booking)
    db.session.commit()

    result = booking.to_dict()
    result["tests"] = body.get("tests", [])
    result["note"] = "A phlebotomist will collect your sample at home."
    return ok(result, status=201)
