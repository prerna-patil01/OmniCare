"""
Ask Omni. The multi-agent deliberation endpoint.

This is where the product actually happens. Everything else is a health app.
"""

import logging

from flask import Blueprint, request

from ai import ContextBuilder, LLMClient, Orchestrator
from ai.triage_engine import ProbeState, TriageEngine
from extensions import db
from models import Conversation, Finding, TriageRecord, Turn
from services import ConsentService, TriageStore, WearableSync
from ai.population_agg import PopulationAggregator
from ai.calibration import Calibrator
from utils import current_user, ok, error, require_auth

logger = logging.getLogger(__name__)

omni_bp = Blueprint("omni", __name__, url_prefix="/api/omni")

# Wired once. The AI package is storage-agnostic by design — these are the
# adapters that give it a database without polluting it with SQLAlchemy.
_consent = ConsentService()
_store = TriageStore()
_llm = LLMClient()
_population = PopulationAggregator(store=_store)
_calibrator = Calibrator(store=_store)
_orchestrator = Orchestrator(llm=_llm, consent_service=_consent, audit_log=_consent)
_engine = TriageEngine(llm=_llm, orchestrator=_orchestrator)
_builder = ContextBuilder(consent_service=_consent)


def _context_for(user, conversation=None):
    """Assemble everything the agents are permitted to see."""
    vitals = WearableSync().recent(user.id, days=14)
    regional = _population.context_for(user.region)

    return _builder.build(
        user=user,
        profile=user.profile,
        history=user.history,
        lifestyle=user.lifestyle,
        vitals=[v.to_dict() for v in vitals],
        reports=[],
        conversation=conversation.as_context() if conversation else [],
        regional=regional,
        purpose="triage",
    )


@omni_bp.post("/chat")
@require_auth
def chat():
    """
    One turn.

    Returns either the next discriminating question, or — once the picture is
    clear enough — the full MDT verdict, which may be an abstention.
    """
    user = current_user()
    body = request.get_json() or {}

    message = (body.get("message") or "").strip()
    if not message:
        return error("Say something.")

    conversation_id = body.get("conversation_id")

    # ── Conversation ──────────────────────────────────────────────
    if conversation_id:
        conversation = Conversation.query.filter_by(
            id=conversation_id, user_id=user.id
        ).first()
        if not conversation:
            return error("No such conversation.", 404)
    else:
        conversation = Conversation(
            user_id=user.id,
            title=message[:80],
        )
        db.session.add(conversation)
        db.session.flush()

    db.session.add(Turn(conversation_id=conversation.id, role="user", content=message))
    db.session.commit()

    # ── Context ───────────────────────────────────────────────────
    ctx = _context_for(user, conversation)

    # ── Probe or conclude ─────────────────────────────────────────
    state = ProbeState(turns=conversation.turns_used)

    try:
        result = _engine.run(user_id=user.id, context=ctx.to_prompt(), state=state)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Deliberation failed")
        return error(
            "Omni could not complete its review. That is a system failure, "
            "not a reassurance — please see a doctor if you are concerned.",
            500,
        )

    probe = result.get("probe", {})
    conversation.turns_used = probe.get("turns", conversation.turns_used)

    # ── Still probing ─────────────────────────────────────────────
    if result["phase"] == "probing":
        question = probe.get("next_question")

        db.session.add(
            Turn(
                conversation_id=conversation.id,
                role="omni",
                content=question,
                discriminates_between=probe.get("discriminates_between", []),
                why_this_question=probe.get("why_this_question"),
            )
        )
        db.session.commit()

        return ok({
            "phase": "probing",
            "conversation_id": conversation.id,
            "question": question,
            "discriminates_between": probe.get("discriminates_between", []),
            "why_this_question": probe.get("why_this_question"),
            "differentials": probe.get("differentials", []),
            "turns_used": probe.get("turns"),
            "turns_remaining": probe.get("turns_remaining"),
        })

    # ── Concluded ─────────────────────────────────────────────────
    conversation.phase = "concluded"

    condition = (
        (result.get("clinical_term") or "").split(" - ")[0]
        or _primary_condition(result.get("deliberation", []))
    )

    # Calibration: adjust confidence based on how honest Omni has been for
    # THIS patient in THIS domain, and say so.
    raw_confidence = result.get("confidence", 0.0)
    domain = Calibrator._domain(condition)  # noqa: SLF001
    adjusted, note = _calibrator.adjust(raw_confidence, domain, user.id)

    record = TriageRecord(
        user_id=user.id,
        conversation_id=conversation.id,
        decision=result.get("decision"),
        conclusion=result.get("conclusion"),
        clinical_term=result.get("clinical_term"),
        condition=condition,
        confidence=adjusted,
        risk_score=result.get("risk_score"),
        risk_band=result.get("risk_band"),
        abstained=result.get("abstained", False),
        abstained_because=result.get("abstained_because"),
        would_resolve_it=result.get("would_resolve_it", []),
        deliberation=result.get("deliberation", []),
        disagreements=result.get("disagreements", []),
        reasoning_trail=result.get("reasoning_trail", []),
        consent_blocks=result.get("consent_blocks", []),
        recommended_action=result.get("recommended_action", {}),
        red_flags=result.get("red_flags", []),
        organ=result.get("organ"),
        human_signoff_required=result.get("human_signoff_required", True),
        region=user.region,
        elapsed_ms=result.get("elapsed_ms"),
    )
    db.session.add(record)

    db.session.add(
        Turn(
            conversation_id=conversation.id,
            role="omni",
            content=result.get("conclusion", ""),
        )
    )

    # ── Pin it to the body ────────────────────────────────────────
    # A finding without a location is a line of text. Pinned to an organ, it
    # becomes a diagram of what is happening inside you.
    if result.get("organ") and not result.get("abstained"):
        db.session.add(
            Finding(
                user_id=user.id,
                organ=result["organ"],
                conclusion=result.get("conclusion"),
                clinical_term=result.get("clinical_term"),
                annotation=(result.get("clinical_term") or "")[:60],
                severity=_severity(result.get("risk_band")),
                risk_score=result.get("risk_score"),
                source="triage",
                source_id=record.id,
            )
        )

    db.session.commit()

    payload = record.to_dict()
    payload["phase"] = "concluded"
    payload["conversation_id"] = conversation.id
    if note:
        payload["calibration_note"] = note

    return ok(payload)


@omni_bp.get("/conversations")
@require_auth
def conversations():
    user = current_user()
    items = (
        Conversation.query.filter_by(user_id=user.id)
        .order_by(Conversation.updated_at.desc())
        .limit(30)
        .all()
    )
    return ok([c.to_dict(include_turns=False) for c in items])


@omni_bp.get("/conversations/<cid>")
@require_auth
def conversation(cid):
    user = current_user()
    c = Conversation.query.filter_by(id=cid, user_id=user.id).first()
    if not c:
        return error("No such conversation.", 404)
    return ok(c.to_dict())


@omni_bp.get("/findings")
@require_auth
def findings():
    """The latest deliberation. What the dashboard hero renders."""
    user = current_user()

    record = (
        TriageRecord.query.filter_by(user_id=user.id)
        .order_by(TriageRecord.created_at.desc())
        .first()
    )

    if not record:
        return ok(None)

    return ok(record.to_dict())


@omni_bp.get("/calibration")
@require_auth
def calibration():
    """
    How honest has Omni been, for this patient, over time?

    An AI that quietly corrects itself is a black box. One that tells you it has
    been overconfident about your GI complaints is a colleague.
    """
    user = current_user()
    return ok(_calibrator.report(user.id).to_dict())


@omni_bp.post("/outcome/<triage_id>")
@require_auth
def outcome(triage_id):
    """
    Ground truth. The ultrasound came back; the doctor said what it actually was.

    This is the fourth quarter of Stimulus → State → Action → Metrics. Most
    systems build three quarters and call the fourth a dashboard.
    """
    from datetime import datetime

    from ai.calibration import Outcome

    user = current_user()
    body = request.get_json() or {}

    record = TriageRecord.query.filter_by(id=triage_id, user_id=user.id).first()
    if not record:
        return error("No such triage record.", 404)

    actual = body.get("actual_condition")
    if not actual:
        return error("actual_condition is required.")

    correct = body.get("correct")
    if correct is None:
        # Rough match — good enough for a demo, insufficient for a real system.
        correct = actual.lower() in (record.condition or "").lower()

    _calibrator.record(
        Outcome(
            triage_id=record.id,
            predicted_condition=record.condition or "",
            predicted_confidence=record.confidence or 0.0,
            predicted_risk=record.risk_score or 0.0,
            actual_condition=actual,
            actual_severity=body.get("actual_severity"),
            confirmed_by=body.get("confirmed_by", "doctor"),
            confirmed_at=datetime.utcnow(),
            correct=bool(correct),
            abstained=bool(record.abstained),
        )
    )

    return ok({
        "recorded": True,
        "calibration": _calibrator.report(user.id).to_dict(),
    })


# ── helpers ───────────────────────────────────────────────────────

def _severity(band):
    return {"low": "low", "medium": "medium", "high": "high", "emergency": "high"}.get(
        band, "low"
    )


def _primary_condition(deliberation):
    triage = next((o for o in deliberation if o.get("agent") == "triage"), None)
    if not triage:
        return ""
    diffs = triage.get("differentials") or []
    if not diffs:
        return ""
    return max(diffs, key=lambda d: d.get("probability", 0)).get("condition", "")


# ── Signoff + dispatch ────────────────────────────────────────────
# The human decision, and the fan-out that follows it. Kept on the omni
# blueprint because signoff is the moment Omni's recommendation becomes a
# human's decision — it belongs next to where the recommendation was made.

from services.dispatch_service import DispatchNotPermitted, DispatchService  # noqa: E402

_dispatch = DispatchService()


@omni_bp.post("/signoff/<triage_id>")
@require_auth
def signoff(triage_id):
    """
    The human decision.

    This is the moment the whole architecture exists to protect. The agents
    advised. A person now decides. There is no code path where the former
    becomes the latter without passing through here — and an abstention cannot
    be signed at all.
    """
    user = current_user()
    body = request.get_json() or {}

    try:
        record = _dispatch.signoff(user, triage_id, body.get("signer", "patient"))
    except DispatchNotPermitted as exc:
        return error(str(exc), 409)

    if not record:
        return error("No such triage record.", 404)

    return ok({
        "signed_off": True,
        "signed_off_by": record.signed_off_by,
        "signed_off_at": record.signed_off_at.isoformat(),
        "triage": record.to_dict(),
    })


@omni_bp.post("/dispatch/<triage_id>")
@require_auth
def dispatch(triage_id):
    """
    Fan out to pharmacy, appointment, care worker, transport.

    Refuses on an unsigned finding. Refuses outright on an abstention — acting on
    an abstention would defeat the entire purpose of having one.
    """
    user = current_user()

    try:
        result = _dispatch.dispatch(user, triage_id)
    except DispatchNotPermitted as exc:
        return error(str(exc), 409)

    return ok(result)
