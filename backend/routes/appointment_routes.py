"""Appointment booking."""

from flask import Blueprint, request

from extensions import db
from models import Appointment, Doctor
from utils import current_user, ok, error, require_auth

appointment_bp = Blueprint("appointments", __name__, url_prefix="/api/appointments")


@appointment_bp.get("")
@require_auth
def list_appointments():
    user = current_user()
    items = (
        Appointment.query.filter_by(user_id=user.id)
        .order_by(Appointment.created_at.desc())
        .all()
    )
    return ok([a.to_dict() for a in items])


@appointment_bp.post("/book")
@require_auth
def book():
    user = current_user()
    body = request.get_json() or {}

    doctor_id = body.get("doctor_id")
    doctor = Doctor.query.get(doctor_id) if doctor_id else None
    if not doctor:
        return error("No such doctor.", 404)

    appt = Appointment(
        user_id=user.id,
        doctor_id=doctor.id,
        mode=body.get("mode", "in_person"),
        slot=body.get("slot", doctor.next_slot),
        status="confirmed",
        triage_id=body.get("triage_id"),
    )
    db.session.add(appt)
    db.session.commit()

    return ok(appt.to_dict(), status=201)


@appointment_bp.post("/<aid>/cancel")
@require_auth
def cancel(aid):
    user = current_user()
    appt = Appointment.query.filter_by(id=aid, user_id=user.id).first()
    if not appt:
        return error("No such appointment.", 404)

    appt.status = "cancelled"
    db.session.commit()
    return ok(appt.to_dict())


# ── Video / voice consultation ────────────────────────────────────

from integrations.video_client import video_room, voice_assist  # noqa: E402


@appointment_bp.get("/<aid>/video")
@require_auth
def video(aid):
    """Generate the video room for an appointment. Live — Jitsi, no key needed."""
    user = current_user()
    appt = Appointment.query.filter_by(id=aid, user_id=user.id).first()
    if not appt:
        return error("No such appointment.", 404)
    doc = appt.doctor.name if appt.doctor else ""
    return ok(video_room(aid, doc))


@appointment_bp.get("/<aid>/voice")
@require_auth
def voice(aid):
    """Voice-call assistance — architected, not yet live."""
    user = current_user()
    appt = Appointment.query.filter_by(id=aid, user_id=user.id).first()
    if not appt:
        return error("No such appointment.", 404)
    return ok(voice_assist(aid))
