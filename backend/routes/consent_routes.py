"""
The Consent Ledger.

This is the demo moment. A judge asks "what if I change my mind?" — you revoke
a grant in front of them, re-run the triage, and the Records agent doesn't run.
The AI visibly becomes less capable, and says so.

Nobody else in the room will be able to do that.
"""

from flask import Blueprint, request

from models import ConsentPurpose, ConsentScope
from services import ConsentService
from utils import current_user, ok, error, require_auth

consent_bp = Blueprint("consent", __name__, url_prefix="/api/consent")

_service = ConsentService()


@consent_bp.get("/ledger")
@require_auth
def ledger():
    """Every grant, active and revoked. The patient's own view of who has what."""
    user = current_user()
    return ok({
        "grants": _service.ledger(user.id),
        "always_permitted": sorted(_service.ALWAYS_PERMITTED),
        "note": (
            "Allergies and blood group are never gated. Withholding them from a "
            "system about to recommend a drug could kill you, and no consent "
            "framework requires that."
        ),
    })


@consent_bp.get("/audit")
@require_auth
def audit():
    """
    Every access, granted and denied.

    Not just the denials. "Who looked at my liver panel and when" needs a complete
    answer, and you cannot reconstruct one from a log that only recorded failures.
    """
    user = current_user()
    return ok(_service.audit_trail(user.id, limit=200))


@consent_bp.post("/grant")
@require_auth
def grant():
    user = current_user()
    body = request.get_json() or {}

    scope = body.get("scope")
    purpose = body.get("purpose", "triage")

    if scope not in [s.value for s in ConsentScope]:
        return error(f"Unknown scope '{scope}'.")
    if purpose not in [p.value for p in ConsentPurpose]:
        return error(f"Unknown purpose '{purpose}'.")

    g = _service.grant(
        user_id=user.id,
        scope=scope,
        purpose=purpose,
        grantee=body.get("grantee"),
        grantee_type=body.get("grantee_type", "omnicare"),
        days=int(body.get("days", 30)),
    )

    return ok(g.to_dict(), status=201)


@consent_bp.post("/revoke/<grant_id>")
@require_auth
def revoke(grant_id):
    """
    Revoke. Effective immediately.

    The next agent that asks for this scope will be refused, and the deliberation
    will show it as a consent block rather than silently degrading.
    """
    user = current_user()
    body = request.get_json() or {}

    g = _service.revoke(user.id, grant_id, body.get("reason"))
    if not g:
        return error("No such grant.", 404)

    return ok({
        "revoked": g.to_dict(),
        "effect": (
            "Effective immediately. Any agent requiring this scope will no longer "
            "run, and Omni will tell you which parts of its reasoning are now unavailable."
        ),
    })


@consent_bp.get("/scopes")
def scopes():
    """The vocabulary. What can be granted, and for what purpose."""
    return ok({
        "scopes": [
            {"value": s.value, "always_permitted": s.value in _service.ALWAYS_PERMITTED}
            for s in ConsentScope
        ],
        "purposes": [p.value for p in ConsentPurpose],
    })
