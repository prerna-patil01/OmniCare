"""
Uber.

There is no client here on purpose. Uber's Rides API is partner-gated — a
business account, an approved use case, and a review process that individual
developers do not clear. We use deep links instead (see integrations/rides.py),
which open the real Uber app with the destination pre-filled and demo better
than an API call would.

This file exists to document that decision, not to hide it.
"""


def deeplink(lat, lng, name):
    from urllib.parse import quote

    return (
        f"uber://?action=setPickup&pickup=my_location"
        f"&dropoff[latitude]={lat}&dropoff[longitude]={lng}"
        f"&dropoff[nickname]={quote(name)}"
    )
