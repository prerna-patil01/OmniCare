from .base import Agent
from ..prompts import LOGISTICS_AGENT


class LogisticsAgent(Agent):
    """
    Routes to the cheapest sufficient level of care.

    This is the agent that expresses OmniCare's actual thesis. India has roughly
    a million ASHA workers and nine hundred thousand doctors, and no system that
    knows which one you need. Over-routing to a specialist is not caution — it is
    a ₹1,200 bill and a three-week wait for something a nurse could have handled
    at your door for ₹340.

    The bottleneck in Indian healthcare is ROUTING, not diagnosis. This agent is
    the routing.
    """

    name = "logistics"
    prompt = LOGISTICS_AGENT

    def _noop(self) -> None:
        pass
