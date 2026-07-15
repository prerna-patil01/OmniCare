"""
OmniCare — Augmented Intelligence Layer.

The organising principle of this package is a claim, not a technique:

    An AI that cannot say "I don't know" is not safe in medicine.

Everything here exists to support that. The agents deliberate, they are
allowed to DISAGREE, and when they do the Adjudicator abstains rather
than picking a winner. A confident wrong answer is worse than an honest
"I need more information" — that is the entire product thesis.

Nothing in this package executes an action. It produces a RECOMMENDATION
PACKAGE that a human signs. Augmented, not agentic — the agents advise
each other; a person decides.
"""

from .orchestrator import Orchestrator, DeliberationResult
from .context_builder import ContextBuilder, PatientContext
from .triage_engine import TriageEngine
from .llm_client import LLMClient
from .report_extractor import ReportExtractor
from .calibration import Calibrator
from .population_agg import PopulationAggregator

__all__ = [
    "Orchestrator",
    "DeliberationResult",
    "ContextBuilder",
    "PatientContext",
    "TriageEngine",
    "LLMClient",
    "ReportExtractor",
    "Calibrator",
    "PopulationAggregator",
]
