"""
Ola.

Ola's developer portal is effectively closed to individual developers — there is
no public signup path. Deep link only, same rationale as Uber.
"""


def deeplink(lat, lng):
    return f"olacabs://app/launch?lat={lat}&lng={lng}&category=mini"
