"""
The shape every agent shares.

An agent that cannot express uncertainty is not an agent, it is an oracle — and
an oracle in medicine is a liability. Confidence is a required field. So is the
ability to say "no relevant contribution."
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AgentOpinion:
    """
    One specialist's independent read.

    `abstained` is not an error state. An agent that correctly recognises the
    case is outside its speciality and says nothing is doing its job perfectly.
    """

    agent: str
    position: str
    confidence: float
    evidence: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    disagrees_with: list[str] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)

    abstained: bool = False
    error: str | None = None

    @property
    def is_confident(self) -> bool:
        """0.6 is the line. Below it, an opinion is a hunch."""
        return self.confidence >= 0.6

    @property
    def is_weak(self) -> bool:
        """Below 0.4, an opinion should not be allowed to move a decision."""
        return self.confidence < 0.4

    def to_dict(self) -> dict:
        return {
            "agent": self.agent,
            "position": self.position,
            "confidence": round(self.confidence, 2),
            "evidence": self.evidence,
            "concerns": self.concerns,
            "disagrees_with": self.disagrees_with,
            "abstained": self.abstained,
            "error": self.error,
            **self.payload,
        }


class Agent(ABC):
    """
    Base class. Every agent gets the same context and answers in isolation.

    The isolation is the point. If the Biometrics agent could see that Triage
    already said "gallstones," it would find a way to agree — models are
    agreeable by construction. Independence is what makes disagreement mean
    something.
    """

    name: str = "agent"
    prompt: str = ""

    def __init__(self, llm, core_system: str):
        self.llm = llm
        self.core_system = core_system

    def deliberate(self, context: str) -> AgentOpinion:
        """
        Form an independent opinion.

        Never raises. An agent that crashes must not take the deliberation with
        it — five opinions and one failure is still a usable MDT. Six failures is
        a system outage, and the Adjudicator will notice that on its own.
        """
        try:
            filled = self.prompt.format(
                core_system=self.core_system,
                context=context,
            )
            raw = self.llm.generate_json(filled)
            return self._parse(raw)

        except Exception as exc:  # noqa: BLE001
            logger.exception("Agent %s failed", self.name)
            return AgentOpinion(
                agent=self.name,
                position="Agent unavailable.",
                confidence=0.0,
                abstained=True,
                error=str(exc),
            )

    def _parse(self, raw: dict) -> AgentOpinion:
        position = raw.get("position", "")

        # An agent that says it has nothing to add is abstaining, and that is a
        # legitimate, valuable answer. Recognise it rather than treating the
        # empty string as a bug.
        abstained = (
            not position
            or "no relevant contribution" in position.lower()
            or raw.get("confidence", 0) == 0
        )

        return AgentOpinion(
            agent=self.name,
            position=position,
            confidence=float(raw.get("confidence", 0.0)),
            evidence=raw.get("evidence", []),
            concerns=raw.get("concerns", []),
            disagrees_with=raw.get("disagrees_with", []),
            abstained=abstained,
            payload={
                k: v
                for k, v in raw.items()
                if k
                not in {
                    "agent",
                    "position",
                    "confidence",
                    "evidence",
                    "concerns",
                    "disagrees_with",
                }
            },
        )

    @abstractmethod
    def _noop(self) -> None:
        """Force subclasses to be explicit. Never called."""
