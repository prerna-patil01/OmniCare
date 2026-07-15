"""
The conversational front door.

Manages the multi-turn probe: asks the discriminating question, tracks turns,
and hands off to the Orchestrator when the picture is clear enough — or when it
has run out of turns, which is itself a finding.

Six turns is a hard cap. A symptom checker that asks forty questions is not being
thorough; it is being lost. If six well-chosen questions have not narrowed it, the
honest answer is "a human needs to look at this," and dragging the patient through
thirty-four more will not change that.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from .llm_client import LLMClient
from .orchestrator import DeliberationResult, Orchestrator
from .prompts import CLINICAL_GUARDRAILS, CORE_SYSTEM, PROBE_FOLLOWUP, TRIAGE_PROBER

logger = logging.getLogger(__name__)

MAX_TURNS = 6


@dataclass
class ProbeState:
    """Where we are in the questioning."""

    turns: int = 0
    differentials: list[dict] = field(default_factory=list)
    next_question: str | None = None
    discriminates_between: list[str] = field(default_factory=list)
    why_this_question: str | None = None
    ready: bool = False
    red_flags: list[str] = field(default_factory=list)

    @property
    def exhausted(self) -> bool:
        return self.turns >= MAX_TURNS

    def to_dict(self) -> dict:
        return {
            "turns": self.turns,
            "differentials": self.differentials,
            "next_question": self.next_question,
            "discriminates_between": self.discriminates_between,
            "why_this_question": self.why_this_question,
            "ready_to_conclude": self.ready,
            "red_flags": self.red_flags,
            "turns_remaining": max(0, MAX_TURNS - self.turns),
        }


class TriageEngine:
    """
    Runs the probe, then convenes the MDT.

    The engine never concludes on its own. It gathers, and then it hands the
    gathered picture to six specialists who argue about it. That separation is
    deliberate: the thing that asks the questions should not also be the thing
    that decides it has heard enough.
    """

    def __init__(self, llm: LLMClient | None = None, orchestrator: Orchestrator | None = None):
        self.llm = llm or LLMClient()
        self.orchestrator = orchestrator or Orchestrator(llm=self.llm)

    def probe(self, context: str, state: ProbeState | None = None) -> ProbeState:
        """
        Ask the next most discriminating question.

        A red flag short-circuits everything. If someone mentions crushing chest
        pain, we do not continue politely gathering history — we stop and escalate.
        Every further question is a delay, and delay is the thing that kills people
        in a myocardial infarction.
        """
        state = state or ProbeState()

        try:
            raw = self.llm.generate_json(
                TRIAGE_PROBER.format(
                    core_system=CORE_SYSTEM,
                    guardrails=CLINICAL_GUARDRAILS,
                    context=context,
                )
            )
        except Exception:  # noqa: BLE001
            logger.exception("Probe failed")
            # A failed probe means we cannot safely continue asking questions.
            # Route to a human rather than guessing at the next one.
            state.ready = True
            return state

        state.turns += 1
        state.differentials = raw.get("differentials", [])
        state.next_question = raw.get("next_question")
        state.discriminates_between = raw.get("discriminates_between", [])
        state.why_this_question = raw.get("why_this_question")
        state.red_flags = raw.get("red_flags_present", [])

        # Red flags end the conversation. Immediately.
        if state.red_flags:
            state.ready = True
            state.next_question = None
            return state

        state.ready = bool(raw.get("ready_to_conclude")) or state.exhausted

        return state

    def conclude(self, user_id: str, context: str) -> DeliberationResult:
        """Hand the gathered picture to the MDT."""
        return self.orchestrator.deliberate(user_id=user_id, context=context)

    def run(self, user_id: str, context: str, state: ProbeState | None = None):
        """
        One turn of the whole loop.

        Returns either the next question, or the MDT's verdict. The caller does
        not need to know which phase we are in — the shape of the response tells
        it.
        """
        state = self.probe(context, state)

        if state.ready:
            result = self.conclude(user_id, context)
            return {"phase": "concluded", "probe": state.to_dict(), **result.to_dict()}

        return {"phase": "probing", "probe": state.to_dict()}
