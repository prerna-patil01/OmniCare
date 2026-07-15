"""
OpenRouteService. Free, no card, real routing.

Google Maps would work too, but it needs a credit card on file and we do not
need a places database — five real hospitals with real coordinates is entirely
sufficient for a demo, and nobody will know the difference.
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

ORS_BASE = "https://api.openrouteservice.org/v2"


class MapsClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("ORS_API_KEY", "")

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def route(self, from_lat, from_lng, to_lat, to_lng, profile="driving-car"):
        """
        Real travel time. Not straight-line distance.

        The difference matters: a hospital 2km away across a river might be a
        25-minute drive, and telling someone in pain that it is "2km" when it is
        25 minutes is a small, avoidable cruelty.
        """
        if not self.available:
            return self._estimate(from_lat, from_lng, to_lat, to_lng)

        try:
            response = requests.get(
                f"{ORS_BASE}/directions/{profile}",
                params={
                    "api_key": self.api_key,
                    "start": f"{from_lng},{from_lat}",
                    "end": f"{to_lng},{to_lat}",
                },
                timeout=8,
            )
            response.raise_for_status()
            data = response.json()

            summary = data["features"][0]["properties"]["summary"]
            return {
                "distance_km": round(summary["distance"] / 1000, 1),
                "duration_min": round(summary["duration"] / 60),
                "source": "openrouteservice",
            }

        except Exception:  # noqa: BLE001
            logger.exception("ORS routing failed — falling back to estimate")
            return self._estimate(from_lat, from_lng, to_lat, to_lng)

    @staticmethod
    def _estimate(from_lat, from_lng, to_lat, to_lng):
        """
        Haversine, then a 1.4× road-factor and a 22 km/h urban average.

        Honest fallback. Labelled as an estimate so nobody mistakes it for a
        real route.
        """
        from math import asin, cos, radians, sin, sqrt

        R = 6371
        dlat = radians(to_lat - from_lat)
        dlng = radians(to_lng - from_lng)
        a = (
            sin(dlat / 2) ** 2
            + cos(radians(from_lat)) * cos(radians(to_lat)) * sin(dlng / 2) ** 2
        )
        straight = 2 * R * asin(sqrt(a))
        road = straight * 1.4

        return {
            "distance_km": round(road, 1),
            "duration_min": round((road / 22) * 60),
            "source": "estimate",
        }
