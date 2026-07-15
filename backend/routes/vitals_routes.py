"""Wearable telemetry."""

from flask import Blueprint, request

from services import WearableSync
from utils import current_user, ok, error, require_auth

vitals_bp = Blueprint("vitals", __name__, url_prefix="/api/vitals")

_sync = WearableSync()


@vitals_bp.get("")
@require_auth
def latest():
    """
    Latest reading plus a 14-day trend.

    The trend matters more than the value. 72 bpm is unremarkable. 72 bpm in
    someone whose baseline is 64 is a signal — and it is a signal no annual
    check-up would ever catch.
    """
    user = current_user()

    latest = _sync.latest(user.id)
    if not latest:
        return ok({"latest": None, "trend": {}, "history": []})

    history = _sync.recent(user.id, days=14)

    return ok({
        "latest": latest.to_dict(),
        "trend": _trend(history),
        "history": [v.to_dict() for v in history],
    })


@vitals_bp.post("/ingest")
@require_auth
def ingest():
    """Webhook. Anything that can POST JSON can feed this."""
    user = current_user()
    body = request.get_json() or {}

    reading = _sync.ingest(user.id, body, source=body.get("source", "webhook"))
    return ok(reading.to_dict(), status=201)


@vitals_bp.post("/seed")
@require_auth
def seed():
    """
    Generate a demo stream with a real clinical signal in it.

    Resting HR drifts up 8%, HRV drifts down 18% — a febrile response the patient
    has not noticed. The demo works because the data actually contains the thing
    the AI claims to find.
    """
    user = current_user()
    count = _sync.seed_stream(user.id, days=14)
    return ok({"readings": count})


def _trend(history):
    if len(history) < 6:
        return {}

    out = {}
    third = max(1, len(history) // 3)

    for key in ("heart_rate", "hrv", "spo2", "sleep_hours"):
        values = [getattr(v, key) for v in history if getattr(v, key) is not None]
        if len(values) < 6:
            continue

        early = sum(values[:third]) / third
        late = sum(values[-third:]) / third

        if early == 0:
            continue

        delta = ((late - early) / early) * 100

        out[key] = {
            "direction": "stable" if abs(delta) < 5 else ("up" if delta > 0 else "down"),
            "pct": round(abs(delta), 1),
            "label": "stable"
            if abs(delta) < 5
            else f"{'up' if delta > 0 else 'down'} {abs(delta):.0f}% over 14d",
        }

    return out


# ── Wearable OAuth (Fitbit / Google Fit) ──────────────────────────

from services.wearable_sync import WearableOAuth  # noqa: E402
from flask import current_app  # noqa: E402


@vitals_bp.get("/connect/<provider>")
@require_auth
def connect(provider):
    """
    Begin a wearable connection. Returns the OAuth URL (architected).

    Fitbit and Google Fit are stubbed with honest status; the synthetic stream
    carries the real signal so nothing downstream breaks.
    """
    client_id = current_app.config.get("GOOGLE_CLIENT_ID", "")
    return ok(WearableOAuth.connect_url(provider, client_id))


@vitals_bp.post("/connect/<provider>/complete")
@require_auth
def connect_complete(provider):
    """After the (stubbed) OAuth, seed the stream as if the device connected."""
    user = current_user()
    count = WearableOAuth.sync_after_auth(user.id, provider)
    return ok({"connected": provider, "readings_synced": count})
