"""
OmniCare backend.

    python app.py    →  http://localhost:5000

Boots, seeds, and serves. If GEMINI_API_KEY is missing the AI layer runs in mock
mode — the app still works, which matters, because a rate limit at 4pm on demo
day should not be able to kill your product.
"""

import logging
import os

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("omnicare")


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    CORS(
        app,
        origins=app.config["CORS_ORIGINS"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
    )

    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    # Registered here, not at import time — blueprints import models, models
    # import db, and db needs the app. Order matters.
    from routes import BLUEPRINTS

    for bp in BLUEPRINTS:
        app.register_blueprint(bp)

    # ── Health check ──────────────────────────────────────────────
    @app.get("/api/health")
    def health():
        return jsonify({
            "ok": True,
            "service": "omnicare",
            "ai": "live" if app.config["GEMINI_API_KEY"] else "mock",
            "maps": "live" if app.config["ORS_API_KEY"] else "estimate",
            "demo_mode": app.config["DEMO_MODE"],
        })

    # ── Errors ────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"ok": False, "error": "No such endpoint."}), 404

    @app.errorhandler(413)
    def too_large(_):
        return jsonify({"ok": False, "error": "That file is too large (max 16 MB)."}), 413

    @app.errorhandler(500)
    def server_error(exc):
        log.exception("Unhandled error")
        return jsonify({"ok": False, "error": "Something broke on our side."}), 500

    return app


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        from seed import seed_all
        seed_all()

    ai_mode = "LIVE" if Config.GEMINI_API_KEY else "MOCK (set GEMINI_API_KEY)"

    print("\n" + "─" * 62)
    print("  OmniCare — Healthcare Operating System")
    print("─" * 62)
    print(f"  API      http://localhost:5000")
    print(f"  Health   http://localhost:5000/api/health")
    print(f"  AI       {ai_mode}")
    print(f"  Maps     {'LIVE' if Config.ORS_API_KEY else 'ESTIMATE'}")
    print(f"  Demo     {Config.DEMO_MODE}  (no login required)")
    print("─" * 62 + "\n")

    app.run(debug=Config.DEBUG, port=5000)
