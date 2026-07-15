"""Pharmacy search + order."""

from flask import Blueprint, request

from extensions import db
from models import Medicine, PharmacyOrder
from utils import current_user, ok, require_auth

pharmacy_bp = Blueprint("pharmacy", __name__, url_prefix="/api/pharmacy")


@pharmacy_bp.get("/search")
def search():
    query = request.args.get("q", "")
    q = Medicine.query

    if query:
        q = q.filter(
            Medicine.name.ilike(f"%{query}%") | Medicine.generic.ilike(f"%{query}%")
        )

    return ok([m.to_dict() for m in q.limit(30).all()])


@pharmacy_bp.post("/order")
@require_auth
def order():
    user = current_user()
    body = request.get_json() or {}

    items = body.get("items", [])
    total = sum(i.get("price_inr", 0) or 0 for i in items)

    o = PharmacyOrder(
        user_id=user.id,
        items=items,
        total_inr=total,
        status="routed",
        eta=body.get("eta", "Today, 7:40 PM"),
        triage_id=body.get("triage_id"),
    )
    db.session.add(o)
    db.session.commit()

    return ok(o.to_dict(), status=201)


@pharmacy_bp.get("/orders")
@require_auth
def orders():
    user = current_user()
    items = (
        PharmacyOrder.query.filter_by(user_id=user.id)
        .order_by(PharmacyOrder.created_at.desc())
        .all()
    )
    return ok([o.to_dict() for o in items])
