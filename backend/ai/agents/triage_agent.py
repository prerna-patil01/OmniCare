from .base import Agent
from ..prompts import TRIAGE_AGENT


class TriageAgent(Agent):
    """
    Reads symptoms, holds differentials, resists collapsing them too early.

    The failure mode this agent guards against is premature closure — the single
    most common diagnostic error in human medicine. A clinician latches onto the
    first plausible explanation and stops looking. This agent is explicitly asked
    to hold several at once, with probabilities, and to keep them open.
    """

    name = "triage"
    prompt = TRIAGE_AGENT

    def _noop(self) -> None:
        pass
