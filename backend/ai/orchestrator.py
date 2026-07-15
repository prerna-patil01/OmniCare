"""
The conductor.

Runs the MDT: consent gate, then six agents IN PARALLEL, then adjudication.

The parallelism is not a performance optimisation — though it is that too. It is
a correctness property. Agents that run sequentially and see each other's output
converge, because language models are agreeable. Six agents that agreed because
they were allowed to read each other are one agent wearing six hats.

Independence is what makes disagreement mean anything.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .agents import (
    Adjudicator,
    AgentOpinion,
    BiometricsAgent,
    ConsentAgent,
    LogisticsAgent,
    PharmacyAgent,
    PopulationAgent,
    RecordsAgent,
    TriageAgent,
    Verdict,
)
from .llm_client import LLMClient
from .prompts import CORE_SYSTEM

logger = logging.getLogger(__name__)


@dataclass
class DeliberationResult:
    """Everything the UI needs to show HOW the conclusion was reached."""

    verdict: Verdict
    opinions: list[AgentOpinion] = field(default_factory=list)
    consent_blocks: list[dict] = field(default_factory=list)
    elapsed_ms: int = 0
    at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            **self.verdict.to_dict(),
            "consent_blocks": self.consent_blocks,
            "elapsed_ms": self.elapsed_ms,
            "at": self.at.isoformat(),
        }


class Orchestrator:
    """
    The multi-disciplinary team meeting, in code.

    Flow:
        1. Consent gate    — agents without permission never run
        2. Parallel MDT    — six independent opinions, no cross-talk
        3. Adjudication    — converge, weigh, or ABSTAIN
        4. Human signoff   — nothing executes without it

    Step 4 is the thesis. The agents advise. A person decides. There is no code
    path in this system where an agent's conclusion becomes an action without a
    human in between, and that is not an oversight to be fixed later.
    """

    def __init__(
        self,
        llm: LLMClient | None = None,
        consent_service: Any = None,
        audit_log: Any = None,
    ):
        self.llm = llm or LLMClient()

        self.consent = ConsentAgent(consent_service=consent_service, audit_log=audit_log)

        self.agents = [
            TriageAgent(self.llm, CORE_SYSTEM),
            RecordsAgent(self.llm, CORE_SYSTEM),
            BiometricsAgent(self.llm, CORE_SYSTEM),
            PharmacyAgent(self.llm, CORE_SYSTEM),
            LogisticsAgent(self.llm, CORE_SYSTEM),
            PopulationAgent(self.llm, CORE_SYSTEM),
        ]

        self.adjudicator = Adjudicator(self.llm, CORE_SYSTEM)

    # ── Public API ────────────────────────────────────────────────

    def deliberate(
        self,
        user_id: str,
        context: str,
        purpose: str = "triage",
    ) -> DeliberationResult:
        started = datetime.utcnow()

        # ── 1. Consent gate ───────────────────────────────────────
        permitted, blocks = self._gate(user_id, purpose)

        if not permitted:
            # Every agent was blocked. That is not an error — it is the consent
            # system working exactly as designed, and the honest thing to do is
            # say so plainly rather than degrade quietly into a worse answer.
            return DeliberationResult(
                verdict=Verdict(
                    decision="abstain",
                    conclusion=(
                        "OmniCare cannot review this without access to your health "
                        "record. You can grant access — scoped and time-limited — "
                        "from Privacy & Consent."
                    ),
                    abstained_because="No consent scopes granted.",
                    would_resolve_it=["Grant medical history access in Privacy & Consent."],
                    risk_score=0.0,
                    risk_band="low",
                    human_signoff_required=True,
                ),
                consent_blocks=blocks,
                elapsed_ms=self._ms(started),
            )

        # ── 2. Parallel deliberation ──────────────────────────────
        opinions = self._run_parallel(permitted, context)

        # ── 3. Adjudication ───────────────────────────────────────
        verdict = self.adjudicator.adjudicate(opinions, context)

        return DeliberationResult(
            verdict=verdict,
            opinions=opinions,
            consent_blocks=blocks,
            elapsed_ms=self._ms(started),
        )

    # ── Internals ─────────────────────────────────────────────────

    def _gate(self, user_id: str, purpose: str) -> tuple[list, list[dict]]:
        """
        Filter agents by consent. Blocked agents do not run.

        Note: they do not "run with less data." They do not run. An agent that
        reasons over a partial record without knowing it is partial will produce
        a confident, wrong answer — which is precisely the failure mode this
        entire system exists to prevent.
        """
        permitted = []
        blocks: list[dict] = []

        for agent in self.agents:
            decision = self.consent.check(user_id, agent.name, purpose)

            if decision.granted:
                permitted.append(agent)
            else:
                blocks.append(
                    {
                        "agent": agent.name,
                        "scope": decision.scope,
                        "reason": decision.reason,
                    }
                )
                logger.info("Agent %s blocked: %s", agent.name, decision.reason)

        return permitted, blocks

    def _run_parallel(self, agents: list, context: str) -> list[AgentOpinion]:
        """
        Six calls, concurrently.

        One agent failing must not take the others with it. Five opinions and a
        failure is a usable MDT. The Adjudicator will see the gap and weigh it.
        """
        opinions: list[AgentOpinion] = []

        with ThreadPoolExecutor(max_workers=len(agents)) as pool:
            futures = {pool.submit(a.deliberate, context): a for a in agents}

            for future in as_completed(futures):
                agent = futures[future]
                try:
                    opinions.append(future.result(timeout=45))
                except Exception as exc:  # noqa: BLE001
                    logger.exception("Agent %s crashed", agent.name)
                    opinions.append(
                        AgentOpinion(
                            agent=agent.name,
                            position="Agent failed to respond.",
                            confidence=0.0,
                            abstained=True,
                            error=str(exc),
                        )
                    )

        # Stable order so the UI does not reshuffle between runs — a deliberation
        # panel whose rows jump around reads as unserious.
        order = {a.name: i for i, a in enumerate(self.agents)}
        opinions.sort(key=lambda o: order.get(o.agent, 99))

        return opinions

    @staticmethod
    def _ms(started: datetime) -> int:
        return int((datetime.utcnow() - started).total_seconds() * 1000)
