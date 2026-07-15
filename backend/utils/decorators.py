"""
Route decorators.

@requires_consent is the gate. A route wrapped in it will not execute its body
until the consent service confirms the scope is granted — the enforcement point
that makes 'consent as a first-class object' real rather than decorative.
"""

from functools import wraps

from flask import request

from services import ConsentService
from utils.auth import current_user
from utils.responses import error

_consent = ConsentService()


def requires_consent(scope, purpose="triage"):
    """
    Block a route unless the caller has granted `scope` for `purpose`.

    Usage:
        @app.get("/api/something")
        @requires_consent("medical_history")
        def something(): ...
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = current_user()
            if not user:
                return error("Authentication required.", 401)

            grant = _consent.get_grant(user.id, scope, purpose)
            if not grant or not grant.active:
                return error(
                    f"This action needs consent for '{scope}'. "
                    "Grant it in Privacy & Consent.",
                    403,
                    missing_scope=scope,
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def json_required(fn):
    """Reject a request that should carry JSON but doesn't."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return error("This endpoint expects a JSON body.", 415)
        return fn(*args, **kwargs)

    return wrapper
