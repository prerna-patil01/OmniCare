"""Configuration. Everything secret comes from the environment, nothing is hardcoded."""

import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # ── Core ──────────────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = ENV == "development"

    # ── Database ──────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'omnicare.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Auth ──────────────────────────────────────────────────────
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-change-me")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRY = timedelta(days=7)

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

    # ── AI ────────────────────────────────────────────────────────
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # ── Maps / routing ────────────────────────────────────────────
    ORS_API_KEY = os.getenv("ORS_API_KEY", "")

    # ── CORS ──────────────────────────────────────────────────────
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

    # ── Uploads ───────────────────────────────────────────────────
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}

    # ── Demo ──────────────────────────────────────────────────────
    # A hackathon has three minutes and no time for a signup flow. The demo
    # user is seeded and auto-authenticated. Real auth exists and works —
    # it just isn't in the critical path of the pitch.
    DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
    DEMO_USER_EMAIL = "prerna@omnicare.health"
