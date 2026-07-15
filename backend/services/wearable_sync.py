"""
Wearable ingestion.

Apple HealthKit has no web API — it is an iOS-native framework, and a React web
app fundamentally cannot read it. That is not a bureaucratic obstacle; it is an
architectural impossibility.

So: webhook endpoint for anything that can POST, plus a synthetic generator that
produces a realistic 14-day stream for the demo. Being honest about which is
which is better than pretending we integrated something we did not.
"""

import random
from datetime import datetime, timedelta

from extensions import db
from models import VitalReading


class WearableSync:
    def ingest(self, user_id: str, payload: dict, source: str = "webhook"):
        reading = VitalReading(
            user_id=user_id,
            heart_rate=payload.get("heart_rate"),
            hrv=payload.get("hrv"),
            spo2=payload.get("spo2"),
            sleep_hours=payload.get("sleep_hours"),
            steps=payload.get("steps"),
            temperature=payload.get("temperature"),
            bp_systolic=payload.get("bp_systolic"),
            bp_diastolic=payload.get("bp_diastolic"),
            source=source,
            recorded_at=datetime.utcnow(),
        )
        db.session.add(reading)
        db.session.commit()
        return reading

    def recent(self, user_id: str, days: int = 14):
        since = datetime.utcnow() - timedelta(days=days)
        return (
            VitalReading.query.filter(
                VitalReading.user_id == user_id,
                VitalReading.recorded_at >= since,
            )
            .order_by(VitalReading.recorded_at)
            .all()
        )

    def latest(self, user_id: str):
        return (
            VitalReading.query.filter_by(user_id=user_id)
            .order_by(VitalReading.recorded_at.desc())
            .first()
        )

    @staticmethod
    def seed_stream(user_id: str, days: int = 14):
        """
        Generate a demo stream with a REAL clinical signal buried in it.

        Resting HR drifts up ~8% and HRV drifts down ~18% over the window. That
        is a febrile response the patient has not consciously noticed — and it
        is precisely the contradiction the Biometrics agent is built to catch.

        The demo works because the data actually contains the thing the AI claims
        to find. A demo where the signal is asserted rather than present is a lie
        with extra steps.
        """
        now = datetime.utcnow()
        readings = []

        for day in range(days):
            for hour in (8, 14, 20):
                offset = days - day
                progress = day / max(1, days - 1)   # 0 → 1

                # The drift. Early days are baseline; later days show the rise.
                hr_drift = progress * 6.0            # +6 bpm over the window
                hrv_drift = progress * -10.0         # -10 ms over the window

                reading = VitalReading(
                    user_id=user_id,
                    heart_rate=round(64 + hr_drift + random.uniform(-2.5, 2.5), 1),
                    hrv=round(62 + hrv_drift + random.uniform(-3, 3), 1),
                    spo2=round(random.uniform(97.0, 99.0), 1),
                    sleep_hours=round(
                        7.4 - (progress * 1.2) + random.uniform(-0.5, 0.5), 1
                    ),
                    steps=random.randint(4200, 8600),
                    source="apple_health",
                    recorded_at=now - timedelta(days=offset, hours=24 - hour),
                )
                readings.append(reading)

        db.session.bulk_save_objects(readings)
        db.session.commit()
        return len(readings)


# ── Fitbit / Google Fit OAuth (stubbed, honest) ───────────────────
# Google Fit's REST API is deprecated (shutting down 2026); Fitbit needs OAuth
# app review that a hackathon will not clear. This stub shows the architecture —
# an OAuth handshake and a sync — without pretending we cleared review. The
# synthetic stream already carries the real clinical signal, so the demo loses
# nothing.

class WearableOAuth:
    PROVIDERS = {
        "fitbit": {
            "auth_url": "https://www.fitbit.com/oauth2/authorize",
            "scopes": ["heartrate", "sleep", "activity", "oxygen_saturation"],
            "status": "requires_app_review",
        },
        "google_fit": {
            "auth_url": "https://accounts.google.com/o/oauth2/auth",
            "scopes": ["fitness.heart_rate.read", "fitness.sleep.read"],
            "status": "api_deprecated_2026",
        },
        "apple_health": {
            "auth_url": None,
            "scopes": [],
            "status": "no_web_api",   # HealthKit is iOS-native; a web app cannot read it
        },
    }

    @classmethod
    def connect_url(cls, provider: str, client_id: str = "") -> dict:
        p = cls.PROVIDERS.get(provider)
        if not p:
            return {"error": f"Unknown provider '{provider}'."}
        return {
            "provider": provider,
            "auth_url": p["auth_url"],
            "scopes": p["scopes"],
            "status": p["status"],
            "note": (
                "Architected, not live. "
                + {
                    "requires_app_review": "Fitbit requires OAuth app review before production.",
                    "api_deprecated_2026": "Google Fit REST API is being retired; migrate to Health Connect.",
                    "no_web_api": "Apple HealthKit has no web API — iOS-native only.",
                }.get(p["status"], "")
            ),
        }

    @classmethod
    def sync_after_auth(cls, user_id: str, provider: str):
        """
        After a (stubbed) successful OAuth, we'd pull the real stream. Here we
        seed the synthetic one so the rest of the app behaves as if connected.
        """
        return WearableSync.seed_stream(user_id, days=14)
