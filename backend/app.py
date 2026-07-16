"""
OmniCare backend.

    python app.py    →  http://localhost:5000

Boots and serves the OmniCare API.
"""

import logging
import os

from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import inspect, text

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
        resources={r"/api/*": {"origins": r"http://localhost:*"}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    )

    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    # Registered here, not at import time — blueprints import models, models
    # import db, and db needs the app. Order matters.
    from routes import BLUEPRINTS

    for bp in BLUEPRINTS:
        app.register_blueprint(bp)

    # Initialise the local schema for all supported startup modes (script, WSGI,
    # and Flask CLI). Blueprint registration above imports every model first.
    with app.app_context():
        db.create_all()
        # This project predates migrations. Keep existing local SQLite installs
        # compatible with the credential field added for verified login.
        if db.engine.dialect.name == "sqlite":
            columns = {column["name"] for column in inspect(db.engine).get_columns("users")}
            if "password_hash" not in columns:
                with db.engine.begin() as connection:
                    connection.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))

    # ── Health check ──────────────────────────────────────────────
    @app.get("/api/health")
    def health():
        return jsonify({
            "ok": True,
            "service": "omnicare",
            "ai": "configured" if app.config["GEMINI_API_KEY"] else "not_configured",
            "maps": "live" if app.config["ORS_API_KEY"] else "estimate",
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
    ai_mode = "CONFIGURED" if Config.GEMINI_API_KEY else "NOT CONFIGURED (set GEMINI_API_KEY)"

    print("\n" + "─" * 62)
    print("  OmniCare — Healthcare Operating System")
    print("─" * 62)
    print(f"  API      http://localhost:5000")
    print(f"  Health   http://localhost:5000/api/health")
    print(f"  AI       {ai_mode}")
    print(f"  Maps     {'LIVE' if Config.ORS_API_KEY else 'ESTIMATE'}")
    print("─" * 62 + "\n")

    app.run(debug=Config.DEBUG, port=5000)
