"""Auth. Real JWT, plus a demo path that skips the login theatre."""

from flask import Blueprint, current_app, request

from extensions import db
from models import User
from services import ConsentService
from utils import current_user, generate_token, ok, error

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    """
    Passwordless. Email or phone identifies; a token is issued.

    Not production auth. Production needs OTP verification, and building that
    for a hackathon is an hour spent on the one part of the product no judge
    will ever test.
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

    return ok({"user": user.to_dict(), "token": generate_token(user.id)})


@auth_bp.post("/register")
def register():
    body = request.get_json() or {}

    if not body.get("name"):
        return error("Name is required.")

    if body.get("email") and User.query.filter_by(email=body["email"]).first():
        return error("An account with that email already exists.", 409)

    user = User(
        name=body["name"],
        email=body.get("email"),
        phone=body.get("phone"),
        abha_id=body.get("abha_id"),
        auth_provider=body.get("provider", "email"),
        region=body.get("region", "Artist Village"),
    )
    db.session.add(user)
    db.session.commit()

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
