"""
The Autonomous Agent — plan, commit, execute.

POST /api/agent/plan/<triage_id>     → agent stages a full action bundle
POST /api/agent/commit/<plan_id>     → the ONE human tap
GET  /api/agent/plan/<plan_id>       → inspect a staged plan
GET  /api/agent/plans                → all plans for the user

The flow: Omni concludes → agent plans autonomously → everything reversible is
staged → human taps commit → agent executes. The tap is the only human moment,
and it exists on purpose.
"""

from datetime import datetime

from flask import Blueprint, request

from ai.autonomous_agent import REQUIRE_COMMIT, AutonomousAgent
from extensions import db
from models import ActionPlan, DigitalTwin, TriageRecord
from services import DispatchService
from utils import current_user, ok, error, require_auth

agent_bp = Blueprint("agent", __name__, url_prefix="/api/agent")

_agent = AutonomousAgent(dispatch_service=DispatchService())


@agent_bp.post("/plan/<triage_id>")
@require_auth
def plan(triage_id):
    """
    The agent reads the verdict + the twin and stages a complete bundle.

    Autonomous — no human input to the planning. Returns the staged plan; nothing
    has executed. The response tells the UI exactly what the commit tap will fire.
    """
    user = current_user()

    record = TriageRecord.query.filter_by(id=triage_id, user_id=user.id).first()
    if not record:
        return error("No such triage record.", 404)

    twin = (
        DigitalTwin.query.filter_by(user_id=user.id)
        .order_by(DigitalTwin.created_at.desc())
        .first()
    )

    plan_dict = _agent.plan(record.to_dict(), twin.to_dict() if twin else None)

    plan_record = ActionPlan(
        user_id=user.id,
        triage_id=triage_id,
        goal=plan_dict["goal"],
        steps=plan_dict["steps"],
        reasoning=plan_dict["reasoning"],
        total_cost_inr=plan_dict["total_cost_inr"],
        status="staged",
    )
    db.session.add(plan_record)
    db.session.commit()

    payload = plan_record.to_dict()
    payload["requires_commit"] = REQUIRE_COMMIT
    return ok(payload, status=201)


@agent_bp.post("/commit/<plan_id>")
@require_auth
def commit(plan_id):
    """
    The one human tap.

    This is the moment the whole architecture protects. Everything up to here was
    autonomous; this is the human saying yes. After this, the agent executes the
    irreversible steps.
    """
    user = current_user()
    body = request.get_json() or {}

    plan_record = ActionPlan.query.filter_by(id=plan_id, user_id=user.id).first()
    if not plan_record:
        return error("No such plan.", 404)

    if plan_record.status == "executed":
        return error("This plan has already been executed.", 409)

    plan_record.committed_at = datetime.utcnow()
    plan_record.committed_by = body.get("signer", "patient")
    plan_record.status = "committed"

    for step in plan_record.steps or []:
        step["status"] = "committed"
    db.session.commit()

    # Execute
    result = _agent.execute(user, plan_record)
    plan_record.status = "executed"
    plan_record.executed_at = datetime.utcnow()
    plan_record.execution_result = result
    db.session.commit()

    return ok({
        "committed": True,
        "executed": result.get("executed", False),
        "plan": plan_record.to_dict(),
    })


@agent_bp.post("/dismiss/<plan_id>")
@require_auth
def dismiss(plan_id):
    """The human declines. Nothing irreversible happened, so nothing to undo."""
    user = current_user()
    plan_record = ActionPlan.query.filter_by(id=plan_id, user_id=user.id).first()
    if not plan_record:
        return error("No such plan.", 404)

    plan_record.status = "dismissed"
    db.session.commit()
    return ok({"dismissed": True})


@agent_bp.get("/plan/<plan_id>")
@require_auth
def get_plan(plan_id):
    user = current_user()
    plan_record = ActionPlan.query.filter_by(id=plan_id, user_id=user.id).first()
    if not plan_record:
        return error("No such plan.", 404)
    return ok(plan_record.to_dict())


@agent_bp.get("/plans")
@require_auth
def plans():
    user = current_user()
    items = (
        ActionPlan.query.filter_by(user_id=user.id)
        .order_by(ActionPlan.staged_at.desc())
        .limit(20)
        .all()
    )
    return ok([p.to_dict() for p in items])
