"""
The Digital Twin — its own page.

GET  /api/twin            → the current twin (computes if stale)
POST /api/twin/recompute  → force a fresh projection
GET  /api/twin/history    → past twins, to show drift over time
"""

from datetime import datetime, timedelta

from ai.llm_client import LLMClient
from ai.twin_engine import TwinEngine, TwinInputs
from extensions import db
from models import DigitalTwin
from services import WearableSync
from ai.population_agg import PopulationAggregator
from services import TriageStore
from flask import Blueprint
from utils import current_user, ok, require_auth

twin_bp = Blueprint("twin", __name__, url_prefix="/api/twin")

_engine = TwinEngine(llm=LLMClient())
_wearables = WearableSync()
_population = PopulationAggregator(store=TriageStore())

# A twin older than this is recomputed on read.
STALE_AFTER = timedelta(hours=6)


def _build_inputs(user) -> TwinInputs:
    """Assemble everything the twin is computed from."""
    profile = user.profile
    history = user.history
    lifestyle = user.lifestyle

    vitals = _wearables.recent(user.id, days=14)
    latest = _wearables.latest(user.id)

    # Trend summary (reuse the same logic the dashboard uses)
    trend = {}
    if len(vitals) >= 6:
        third = max(1, len(vitals) // 3)
        for key in ("heart_rate", "hrv", "spo2", "sleep_hours"):
            vals = [getattr(v, key) for v in vitals if getattr(v, key) is not None]
            if len(vals) < 6:
                continue
            early = sum(vals[:third]) / third
            late = sum(vals[-third:]) / third
            if early == 0:
                continue
            delta = ((late - early) / early) * 100
            if abs(delta) >= 5:
                trend[key] = f"{'up' if delta > 0 else 'down'} {abs(delta):.0f}% over 14d"

    return TwinInputs(
        age=profile.age if profile else None,
        sex=profile.gender if profile else None,
        bmi=profile.bmi if profile else None,
        conditions=(history.current_diseases if history else []) or [],
        past_conditions=(history.past_diseases if history else []) or [],
        family_history=(history.family_history if history else []) or [],
        medications=(history.medications if history else []) or [],
        allergies=(history.allergies if history else []) or [],
        smoking=lifestyle.smoking if lifestyle else None,
        alcohol=lifestyle.alcohol if lifestyle else None,
        exercise=lifestyle.exercise if lifestyle else None,
        diet=lifestyle.food_habits if lifestyle else None,
        stress=lifestyle.stress if lifestyle else None,
        hydration_l=lifestyle.hydration_l if lifestyle else None,
        sleep=lifestyle.sleep if lifestyle else None,
        vitals=latest.to_dict() if latest else {},
        vitals_trend=trend,
        abnormal_labs=[],
        regional_signals=_population.context_for(user.region),
    )


def _compute_and_store(user) -> DigitalTwin:
    computed = _engine.compute(_build_inputs(user))
    twin = DigitalTwin(user_id=user.id, **{
        k: computed[k] for k in (
            "health_score", "biological_age", "chronological_age", "trajectory",
            "system_risk", "predispositions", "active_signals", "interventions",
            "confidence", "computed_from", "narrative",
        )
    })
    db.session.add(twin)
    db.session.commit()
    return twin


@twin_bp.get("")
@require_auth
def get_twin():
    """Return the current twin. Recompute if stale or missing."""
    user = current_user()

    latest = (
        DigitalTwin.query.filter_by(user_id=user.id)
        .order_by(DigitalTwin.created_at.desc())
        .first()
    )

    if not latest or (datetime.utcnow() - latest.created_at) > STALE_AFTER:
        latest = _compute_and_store(user)

    return ok(latest.to_dict())


@twin_bp.post("/recompute")
@require_auth
def recompute():
    """Force a fresh projection — e.g. after new vitals or a report upload."""
    user = current_user()
    twin = _compute_and_store(user)
    return ok(twin.to_dict())


@twin_bp.get("/history")
@require_auth
def history():
    """
    Past twins, to show drift.

    Trajectory is the product — "your cardiovascular risk was 3.1 last month, it
    is 3.8 now" is worth more than either number alone.
    """
    user = current_user()
    twins = (
        DigitalTwin.query.filter_by(user_id=user.id)
        .order_by(DigitalTwin.created_at.desc())
        .limit(12)
        .all()
    )
    return ok([
        {
            "created_at": t.created_at.isoformat(),
            "health_score": t.health_score,
            "biological_age": t.biological_age,
            "system_risk": t.system_risk or {},
            "trajectory": t.trajectory,
        }
        for t in twins
    ])
