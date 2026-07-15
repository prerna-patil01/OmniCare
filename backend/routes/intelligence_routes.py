"""
Disease Intelligence. Layer 4.

The signals here are not decorative — they feed back DOWN into individual
triage via the Population Agent. That downward flow is what makes the four-layer
architecture a system rather than a poster.
"""

from flask import Blueprint, request

from ai.population_agg import PopulationAggregator
from services import TriageStore
from utils import current_user, ok

intelligence_bp = Blueprint("intelligence", __name__, url_prefix="/api/intelligence")

_aggregator = PopulationAggregator(store=TriageStore())


@intelligence_bp.get("/regional")
def regional():
    """
    What is going around, here, right now.

    Suppressed below the k-anonymity threshold — in a small enough region,
    "3 dengue cases" plus a postcode is a name.
    """
    user = current_user()
    region = request.args.get("region") or (user.region if user else "Artist Village")

    signals = _aggregator.signals_for(region)

    # Seeded environmental context. In production these come from CPCB and IMD.
    ambient = [
        {
            "label": "Air quality",
            "value": "AQI 118",
            "note": "Moderate — sensitive groups should limit outdoor exertion",
            "tone": "amber",
        },
        {
            "label": "Flu vaccination",
            "value": "Available",
            "note": "3 clinics within 4 km",
            "tone": "green",
        },
    ]

    return ok({
        "region": region,
        "signals": [s.to_dict() for s in signals],
        "ambient": ambient,
        "suppressed": len(signals) == 0,
        "suppression_note": (
            "Signals below 8 cases are not shown. In a small region, three cases "
            "plus a postcode is a name."
        ),
    })
