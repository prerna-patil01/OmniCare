"""
Ride deep links.

No API key, no partner approval, and — genuinely — a better demo than an API
call. The judge watches the real Uber app open with Apollo already set as the
destination. A JSON response claiming a ride was booked proves nothing.
"""

from urllib.parse import quote


def ride_deeplinks(lat: float, lng: float, name: str) -> dict:
    encoded = quote(name)

    return {
        "uber": {
            "app": (
                f"uber://?action=setPickup&pickup=my_location"
                f"&dropoff[latitude]={lat}&dropoff[longitude]={lng}"
                f"&dropoff[nickname]={encoded}"
            ),
            "web": (
                f"https://m.uber.com/ul/?action=setPickup&pickup=my_location"
                f"&dropoff[latitude]={lat}&dropoff[longitude]={lng}"
                f"&dropoff[nickname]={encoded}"
            ),
        },
        "ola": {
            "app": f"olacabs://app/launch?lat={lat}&lng={lng}&category=mini",
            "web": f"https://book.olacabs.com/?drop_lat={lat}&drop_lng={lng}",
        },
        "maps": f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}",
    }
