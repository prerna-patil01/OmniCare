from .base import Agent, AgentOpinion
from ..prompts import BIOMETRICS_AGENT


class BiometricsAgent(Agent):
    """
    The only agent looking at what the patient cannot feel.

    Its most valuable output is a CONTRADICTION. When someone says "no fever" and
    their resting heart rate has climbed 8% over three days while HRV dropped 18%,
    the body is mounting a febrile response the person has not consciously noticed.

    That contradiction is often the entire finding, and no clinician in a
    seven-minute consult would ever catch it.
    """

    name = "biometrics"
    prompt = BIOMETRICS_AGENT

    def _parse(self, raw: dict) -> AgentOpinion:
        opinion = super()._parse(raw)

        # A contradiction between the data and the patient's own account is the
        # highest-value thing this agent can produce. Surface it loudly.
        contradiction = raw.get("contradicts_patient_report")
        if contradiction:
            opinion.concerns.insert(0, f"CONTRADICTION: {contradiction}")

        # Sparse data means low confidence, regardless of what the model claims.
        # A model handed three data points will still happily assert a trend.
        if raw.get("data_quality") in ("sparse", "unavailable"):
            opinion.confidence = min(opinion.confidence, 0.35)

        return opinion

    def _noop(self) -> None:
        pass
