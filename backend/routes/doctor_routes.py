"""Doctor directory + search."""

from flask import Blueprint, request

from models import Doctor
from utils import ok

doctor_bp = Blueprint("doctors", __name__, url_prefix="/api/doctors")


@doctor_bp.get("")
def doctors():
    q = Doctor.query

    specialty = request.args.get("specialty")
    if specialty:
        q = q.filter(Doctor.specialty.ilike(f"%{specialty}%"))

    max_fee = request.args.get("max_fee", type=int)
    if max_fee:
        q = q.filter(Doctor.fee_inr <= max_fee)

    if request.args.get("video") == "true":
        q = q.filter_by(video_available=True)

    sort = request.args.get("sort", "distance")
    order = {
        "distance": Doctor.distance_km,
        "fee": Doctor.fee_inr,
        "rating": Doctor.rating.desc(),
        "experience": Doctor.experience_years.desc(),
    }.get(sort, Doctor.distance_km)

    return ok([d.to_dict() for d in q.order_by(order).all()])


@doctor_bp.get("/search")
def search():
    """Free-text across name, specialty, hospital."""
    term = request.args.get("q", "")
    q = Doctor.query

    if term:
        like = f"%{term}%"
        q = q.filter(
            Doctor.name.ilike(like)
            | Doctor.specialty.ilike(like)
            | Doctor.hospital.ilike(like)
        )

    return ok([d.to_dict() for d in q.order_by(Doctor.distance_km).limit(20).all()])


@doctor_bp.get("/<int:doctor_id>")
def get_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        from utils import error
        return error("No such doctor.", 404)
    return ok(doctor.to_dict())
