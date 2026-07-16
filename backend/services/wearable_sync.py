"""Ingestion and retrieval of verified wearable readings."""

from datetime import datetime, timedelta

from extensions import db
from models import VitalReading


class WearableSync:
    def ingest(self, user_id: str, payload: dict, source: str = "webhook"):
        reading = VitalReading(
            user_id=user_id,
            heart_rate=payload.get("heart_rate"), hrv=payload.get("hrv"),
            spo2=payload.get("spo2"), sleep_hours=payload.get("sleep_hours"),
            steps=payload.get("steps"), temperature=payload.get("temperature"),
            bp_systolic=payload.get("bp_systolic"), bp_diastolic=payload.get("bp_diastolic"),
            source=source, recorded_at=datetime.utcnow(),
        )
        db.session.add(reading); db.session.commit()
        return reading

    def recent(self, user_id: str, days: int = 14):
        since = datetime.utcnow() - timedelta(days=days)
        return VitalReading.query.filter(VitalReading.user_id == user_id, VitalReading.recorded_at >= since).order_by(VitalReading.recorded_at).all()

    def latest(self, user_id: str):
        return VitalReading.query.filter_by(user_id=user_id).order_by(VitalReading.recorded_at.desc()).first()


class WearableOAuth:
    PROVIDERS = {
        "fitbit": {"auth_url": "https://www.fitbit.com/oauth2/authorize", "scopes": ["heartrate", "sleep", "activity", "oxygen_saturation"]},
        "google_fit": {"auth_url": "https://accounts.google.com/o/oauth2/auth", "scopes": ["fitness.heart_rate.read", "fitness.sleep.read"]},
    }

    @classmethod
    def connect_url(cls, provider: str, client_id: str = "") -> dict:
        config = cls.PROVIDERS.get(provider)
        if not config:
            return {"error": f"Unknown or unsupported provider '{provider}'."}
        return {"provider": provider, **config, "client_id_configured": bool(client_id)}
