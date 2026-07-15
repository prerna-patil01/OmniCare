from .base import Agent, AgentOpinion
from ..prompts import RECORDS_AGENT


class RecordsAgent(Agent):
    """
    The memory. History, family risk, and — critically — allergy veto power.

    This is the only agent with a hard veto. If it flags an allergy conflict, no
    downstream agent may override it and the Adjudicator must honour it. That is
    not a design preference; it is the difference between a helpful product and a
    lawsuit.
    """

    name = "records"
    prompt = RECORDS_AGENT

    def _parse(self, raw: dict) -> AgentOpinion:
        opinion = super()._parse(raw)

        # An allergy veto is not an opinion to be weighed. Promote it to a
        # concern so the Adjudicator cannot quietly average it away.
        vetoes = raw.get("allergy_vetoes", [])
        if vetoes:
            opinion.concerns.insert(0, f"ALLERGY VETO: {'; '.join(vetoes)}")
            # A veto is a certainty, not a suggestion.
            opinion.confidence = max(opinion.confidence, 0.95)

        return opinion

    def _noop(self) -> None:
        pass
