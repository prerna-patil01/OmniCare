"""
Ride deep links.

No Uber/Ola API — partner approval takes months. These open the real apps with
the destination pre-filled, which demos better than a JSON receipt anyway. On
desktop they fall through to the web URL so the demo never dead-ends.
"""

from flask import Blueprint, request

from extensions import db
from integrations import MapsClient, ride_deeplinks
from models import Hospital, Ride
from utils import current_user, ok, error, require_auth

ride_bp = Blueprint("rides", __name__, url_prefix="/api/rides")

_maps = MapsClient()


@ride_bp.post("/request")
@require_auth
def request_ride():
    user = current_user()
    body = request.get_json() or {}

    lat = body.get("lat")
    lng = body.get("lng")
    name = body.get("destination", "Hospital")

    # If no explicit destination, route to the nearest hospital
    if lat is None or lng is None:
        hospital = Hospital.query.order_by(Hospital.distance_km).first()
        if not hospital:
            return error("No destination and no hospital on file.", 400)
        lat, lng, name = hospital.lat, hospital.lng, hospital.name

    links = ride_deeplinks(lat, lng, name)

    ride = Ride(
        user_id=user.id,
        destination=name,
        dest_lat=lat,
        dest_lng=lng,
        provider=body.get("provider", "uber"),
        uber_deeplink=links["uber"]["app"],
        ola_deeplink=links["ola"]["app"],
        urgency=body.get("urgency", "scheduled"),
        triage_id=body.get("triage_id"),
    )
    db.session.add(ride)
    db.session.commit()

    payload = ride.to_dict()
    payload["links"] = links
    return ok(payload, status=201)


@ride_bp.get("/eta")
def eta():
    """Real travel time via OpenRouteService, haversine fallback."""
    from_lat = request.args.get("from_lat", type=float)
    from_lng = request.args.get("from_lng", type=float)
    to_lat = request.args.get("to_lat", type=float)
    to_lng = request.args.get("to_lng", type=float)

    if None in (from_lat, from_lng, to_lat, to_lng):
        return error("from_lat, from_lng, to_lat, to_lng are all required.", 400)

    return ok(_maps.route(from_lat, from_lng, to_lat, to_lng))
