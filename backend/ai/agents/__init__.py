"""
The multi-disciplinary team.

Six specialists and an adjudicator. They deliberate the way a hospital MDT
deliberates: independently first, then in the open, and a single accountable
party signs at the end.

The design constraint that matters: the agents run IN PARALLEL and do not see
each other's output. Independent opinions that converge are evidence. Opinions
that were allowed to influence one another are an echo chamber with extra steps.
"""

from .base import Agent, AgentOpinion
from .triage_agent import TriageAgent
from .records_agent import RecordsAgent
from .biometrics_agent import BiometricsAgent
from .pharmacy_agent import PharmacyAgent
from .logistics_agent import LogisticsAgent
from .population_agent import PopulationAgent
from .consent_agent import ConsentAgent, ConsentDenied
from .adjudicator import Adjudicator, Verdict

__all__ = [
    "Agent",
    "AgentOpinion",
    "TriageAgent",
    "RecordsAgent",
    "BiometricsAgent",
    "PharmacyAgent",
    "LogisticsAgent",
    "PopulationAgent",
    "ConsentAgent",
    "ConsentDenied",
    "Adjudicator",
    "Verdict",
]
