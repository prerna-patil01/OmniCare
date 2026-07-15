from .base import Agent, AgentOpinion
from ..prompts import PHARMACY_AGENT


class PharmacyAgent(Agent):
    """
    Medication safety. Default answer: nothing is needed.

    Most symptoms do not need a drug. An agent that suggests one every time is
    not being helpful, it is being a vending machine — and in a country where
    antibiotic over-prescription is a genuine public health crisis, that is an
    actively harmful default.
    """

    name = "pharmacy"
    prompt = PHARMACY_AGENT

    def _parse(self, raw: dict) -> AgentOpinion:
        opinion = super()._parse(raw)

        # If it suggests a drug without stating what it checked allergies
        # against, that suggestion is not trustworthy. Downgrade it.
        if raw.get("suggested") and not raw.get("allergy_check"):
            opinion.concerns.insert(
                0, "Suggested medication without a documented allergy check."
            )
            opinion.confidence = min(opinion.confidence, 0.3)

        return opinion

    def _noop(self) -> None:
        pass
