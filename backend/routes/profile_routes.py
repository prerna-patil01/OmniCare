"""Profile, onboarding, and the health record."""

from datetime import datetime

from flask import Blueprint, request

from extensions import db
from models import HealthProfile, Lifestyle, MedicalHistory
from utils import current_user, ok, error, require_auth

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@profile_bp.get("")
@require_auth
def get_profile():
    user = current_user()

    return ok({
        "user": user.to_dict(),
        "profile": user.profile.to_dict() if user.profile else None,
        "history": user.history.to_dict() if user.history else None,
        "lifestyle": user.lifestyle.to_dict() if user.lifestyle else None,
    })


@profile_bp.post("/onboard")
@require_auth
def onboard():
    """
    The four-step onboarding, committed in one transaction.

    Also seeds the wearable stream — because a health OS with no telemetry on
    day one is just a form you filled in.
    """
    user = current_user()
    body = request.get_json() or {}

    # ── Step 1: personal ──────────────────────────────────────────
    personal = body.get("personal", {})
    profile = user.profile or HealthProfile(user_id=user.id)

    if personal.get("dob"):
        try:
            profile.dob = datetime.fromisoformat(personal["dob"]).date()
        except ValueError:
            return error("Date of birth is not a valid date.")

    profile.gender = personal.get("gender")
    profile.height_cm = _num(personal.get("height"))
    profile.weight_kg = _num(personal.get("weight"))
    profile.blood_group = personal.get("bloodGroup")
    profile.emergency_contact = personal.get("emergencyContact")

    db.session.add(profile)

    # ── Step 2: medical ───────────────────────────────────────────
    medical = body.get("medical", {})
    history = user.history or MedicalHistory(user_id=user.id)

    history.allergies = medical.get("allergies", [])
    history.current_diseases = medical.get("currentDiseases", [])
    history.past_diseases = medical.get("pastDiseases", [])
    history.surgeries = medical.get("surgeries", [])
    history.medications = medical.get("medications", [])
    history.family_history = medical.get("familyHistory", [])

    db.session.add(history)

    # ── Step 3: lifestyle ─────────────────────────────────────────
    life = body.get("lifestyle", {})
    lifestyle = user.lifestyle or Lifestyle(user_id=user.id)

    lifestyle.smoking = life.get("smoking")
    lifestyle.alcohol = life.get("alcohol")
    lifestyle.food_habits = life.get("foodHabits")
    lifestyle.exercise = life.get("exercise")
    lifestyle.stress = life.get("stress")
    lifestyle.sleep = life.get("sleep")
    lifestyle.hydration_l = _num(life.get("hydration"))
    lifestyle.occupation = life.get("occupation")

    db.session.add(lifestyle)

    user.onboarded = True
    db.session.commit()

    connections = body.get("connections", [])
    return ok({"user": user.to_dict(), "connections": connections})


@profile_bp.patch("")
@require_auth
def update_profile():
    user = current_user()
    body = request.get_json() or {}

    if "profile" in body and user.profile:
        for k, v in body["profile"].items():
            if hasattr(user.profile, k):
                setattr(user.profile, k, v)

    if "history" in body and user.history:
        for k, v in body["history"].items():
            if hasattr(user.history, k):
                setattr(user.history, k, v)

    if "lifestyle" in body and user.lifestyle:
        for k, v in body["lifestyle"].items():
            if hasattr(user.lifestyle, k):
                setattr(user.lifestyle, k, v)

    db.session.commit()
    return ok({"user": user.to_dict()})


def _num(value):
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None
