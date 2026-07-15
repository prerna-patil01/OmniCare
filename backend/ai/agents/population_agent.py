from .base import Agent
from ..prompts import POPULATION_AGENT


class PopulationAgent(Agent):
    """
    The base-rate agent. The one that stops everyone else from ignoring Bayes.

    A textbook says right upper quadrant pain suggests gallstones. The textbook
    does not know that dengue is up 12% within four kilometres of this specific
    patient, this week — and that dengue causes hepatitis, which causes exactly
    that pain.

    This agent is the reason the Population Intelligence layer is not a vanity
    dashboard. It feeds back down into the individual diagnosis. That closes the
    loop between Layer 4 and Layer 2, which is the thing the four-layer
    architecture was always claiming to do and rarely does.
    """

    name = "population"
    prompt = POPULATION_AGENT

    def _noop(self) -> None:
        pass
