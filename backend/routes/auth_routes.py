"""Credential authentication and JWT session issuance."""

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import User
from services import ConsentService
from utils import current_user, generate_token, ok, error

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    """
    Email/password login verifies the stored password hash.
    """
    body = request.get_json() or {}
    email = body.get("email")
    phone = body.get("phone")
    abha = body.get("abha_id")

    user = None
    if email:
        user = User.query.filter_by(email=email).first()
    elif phone:
        user = User.query.filter_by(phone=phone).first()
    elif abha:
        user = User.query.filter_by(abha_id=abha).first()

    if not user:
        return error("No account found. Create one first.", 404)

    if email and not user.verify_password(body.get("password") or ""):
        return error("Email or password is incorrect.", 401)
    if not email:
        return error("Phone and ABHA sign-in require a verified identity provider.", 501)

    return ok({"user": user.to_dict(), "token": generate_token(user.id)})


@auth_bp.post("/register")
def register():
    body = request.get_json() or {}

    name = (body.get("name") or "").strip()
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    if not name:
        return error("Name is required.")
    if not email:
        return error("Email is required.")
    if len(password) < 8:
        return error("Password must be at least 8 characters.")
    if User.query.filter_by(email=email).first():
        return error("An account with that email already exists.", 409)
    phone = (body.get("phone") or "").strip() or None
    if phone and User.query.filter_by(phone=phone).first():
        return error("An account with that phone number already exists.", 409)

    user = User(
        name=name,
        email=email,
        phone=phone,
        abha_id=body.get("abha_id"),
        auth_provider=body.get("provider", "email"),
        region=body.get("region", "Artist Village"),
    )
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("An account with those details already exists.", 409)

    # A new user gets scoped, time-boxed consent grants immediately. Not a
    # checkbox — actual grants, visible in the ledger, revocable from day one.
    ConsentService.bootstrap(user.id)

    return ok({"user": user.to_dict(), "token": generate_token(user.id)}, status=201)


@auth_bp.get("/me")
def me():
    user = current_user()
    if not user:
        return error("Not authenticated.", 401)
    return ok({"user": user.to_dict()})


@auth_bp.post("/google")
def google():
    """
    Google OAuth.

    The frontend does the OAuth dance and posts us the verified profile. We
    trust it in demo mode; in production this would verify the id_token against
    Google's certs.
    """
    body = request.get_json() or {}
    email = body.get("email")

    if not email:
        return error("Google profile is missing an email.")

    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            name=body.get("name", "Google User"),
            email=email,
            auth_provider="google",
        )
        db.session.add(user)
        db.session.commit()
        ConsentService.bootstrap(user.id)

    return ok({"user": user.to_dict(), "token": generate_token(user.id)})
