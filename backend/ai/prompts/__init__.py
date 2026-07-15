"""
Prompts live in their own files, not inline in the logic.

Two reasons. First, a prompt is content, not code — a clinician should be
able to read and correct one without touching Python. Second, when triage
quality regresses, you want to `git diff` the prompt, not archaeology
through a service class.
"""

from .system import CORE_SYSTEM, CLINICAL_GUARDRAILS
from .triage_prober import TRIAGE_PROBER, PROBE_FOLLOWUP
from .abstention import ABSTENTION_CHECK, ABSTENTION_RUBRIC
from .report_parser import REPORT_PARSER
from .organ_mapper import ORGAN_MAPPER
from .dispatch_router import DISPATCH_ROUTER
from .adjudicator import ADJUDICATOR
from .agent_prompts import (
    TRIAGE_AGENT,
    RECORDS_AGENT,
    BIOMETRICS_AGENT,
    PHARMACY_AGENT,
    LOGISTICS_AGENT,
    POPULATION_AGENT,
)

__all__ = [
    "CORE_SYSTEM",
    "CLINICAL_GUARDRAILS",
    "TRIAGE_PROBER",
    "PROBE_FOLLOWUP",
    "ABSTENTION_CHECK",
    "ABSTENTION_RUBRIC",
    "REPORT_PARSER",
    "ORGAN_MAPPER",
    "DISPATCH_ROUTER",
    "ADJUDICATOR",
    "TRIAGE_AGENT",
    "RECORDS_AGENT",
    "BIOMETRICS_AGENT",
    "PHARMACY_AGENT",
    "LOGISTICS_AGENT",
    "POPULATION_AGENT",
]
