"""
The fourth quarter of the loop.

Stimulus → State → Action → Metrics. Most systems build the first three and
call the fourth a dashboard. A metric you merely LOG is a dashboard. A metric
that CHANGES THE NEXT ACTION is a system.

This file closes it. When ground truth arrives — the ultrasound result, the
doctor's actual diagnosis — we score what Omni predicted against what was true,
and we adjust future confidence accordingly.

This is NOT model retraining. That needs infrastructure you do not have and
should not build. This is calibration: a stored offset, applied to future
predictions in the same domain. Cheap, honest, and visible to the user.
"""

from __future__ import annotations

import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class Outcome:
    """What actually happened, versus what Omni said would happen."""

    triage_id: str
    predicted_condition: str
    predicted_confidence: float
    predicted_risk: float

    actual_condition: str | None = None
    actual_severity: str | None = None
    confirmed_by: str | None = None
    confirmed_at: datetime | None = None

    correct: bool | None = None
    abstained: bool = False

    @property
    def resolved(self) -> bool:
        return self.actual_condition is not None

    @property
    def overconfident(self) -> bool:
        """Wrong AND sure about it. The worst quadrant to be in."""
        return self.correct is False and self.predicted_confidence >= 0.7

    @property
    def underconfident(self) -> bool:
        """Right, but hedged. Less dangerous, still a miscalibration."""
        return self.correct is True and self.predicted_confidence < 0.5


@dataclass
class CalibrationReport:
    """How honest has Omni been, for this patient, over time?"""

    total: int = 0
    resolved: int = 0
    correct: int = 0
    abstentions: int = 0

    accuracy: float = 0.0
    mean_confidence: float = 0.0
    calibration_gap: float = 0.0      # confidence minus accuracy. Positive = overconfident.

    abstention_rate: float = 0.0
    abstention_precision: float = 0.0  # of abstentions, how many were genuinely ambiguous

    overconfident_count: int = 0
    domain_offsets: dict[str, float] = field(default_factory=dict)

    narrative: str = ""

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "resolved": self.resolved,
            "correct": self.correct,
            "accuracy": round(self.accuracy, 3),
            "mean_confidence": round(self.mean_confidence, 3),
            "calibration_gap": round(self.calibration_gap, 3),
            "abstentions": self.abstentions,
            "abstention_rate": round(self.abstention_rate, 3),
            "abstention_precision": round(self.abstention_precision, 3),
            "overconfident_count": self.overconfident_count,
            "domain_offsets": {k: round(v, 3) for k, v in self.domain_offsets.items()},
            "narrative": self.narrative,
        }


class Calibrator:
    """
    Scores predictions against ground truth and produces a confidence offset.

    The offset is applied to FUTURE predictions in the same domain. If Omni has
    been consistently overconfident about GI complaints for this patient, its next
    GI prediction gets marked down — and the user is TOLD that.

    That last part is the point. An AI that quietly corrects itself is a black box.
    An AI that says "I have been over-weighting post-prandial pain in your case,
    so I am less sure this time" is a colleague.
    """

    # Below 5 samples, any "trend" is noise wearing a hat.
    MIN_SAMPLES = 5

    def __init__(self, store=None):
        self.store = store

    def record(self, outcome: Outcome) -> None:
        if self.store:
            self.store.save_outcome(outcome)

    def report(self, user_id: str, window_days: int = 180) -> CalibrationReport:
        outcomes = self._load(user_id, window_days)

        if not outcomes:
            return CalibrationReport(
                narrative="Not enough history yet. Omni will learn how accurate it "
                          "has been for you as outcomes come in."
            )

        report = CalibrationReport(total=len(outcomes))

        resolved = [o for o in outcomes if o.resolved]
        abstentions = [o for o in outcomes if o.abstained]

        report.resolved = len(resolved)
        report.abstentions = len(abstentions)
        report.abstention_rate = len(abstentions) / len(outcomes)

        scored = [o for o in resolved if o.correct is not None]

        if scored:
            report.correct = sum(1 for o in scored if o.correct)
            report.accuracy = report.correct / len(scored)
            report.mean_confidence = statistics.mean(o.predicted_confidence for o in scored)

            # The single most important number in this file.
            # Positive means Omni is more confident than it deserves to be.
            report.calibration_gap = report.mean_confidence - report.accuracy

            report.overconfident_count = sum(1 for o in scored if o.overconfident)

        # An abstention was "correct" if the eventual diagnosis was NOT the thing
        # the system was leaning toward — i.e. it was right to refuse.
        if abstentions:
            justified = sum(
                1 for o in abstentions
                if o.actual_condition and o.actual_condition != o.predicted_condition
            )
            report.abstention_precision = justified / len(abstentions)

        report.domain_offsets = self._offsets(scored)
        report.narrative = self._narrate(report)

        return report

    def adjust(self, confidence: float, domain: str, user_id: str) -> tuple[float, str | None]:
        """
        Apply the learned offset to a fresh prediction.

        Returns the adjusted confidence AND an explanation, because an unexplained
        adjustment is indistinguishable from a bug.
        """
        report = self.report(user_id)
        offset = report.domain_offsets.get(domain)

        if offset is None or abs(offset) < 0.08:
            return confidence, None

        adjusted = max(0.0, min(1.0, confidence - offset))

        if offset > 0:
            note = (
                f"Omni has been overconfident about {domain} complaints in your case "
                f"({int(offset * 100)}% gap). Confidence adjusted down accordingly."
            )
        else:
            note = (
                f"Omni has been more accurate than it expected on {domain} complaints "
                f"for you. Confidence adjusted up."
            )

        return adjusted, note

    # ── Internals ─────────────────────────────────────────────────

    def _load(self, user_id: str, window_days: int) -> list[Outcome]:
        if not self.store:
            return []
        since = datetime.utcnow() - timedelta(days=window_days)
        return self.store.outcomes_for(user_id=user_id, since=since)

    def _offsets(self, scored: list[Outcome]) -> dict[str, float]:
        """
        Per-domain calibration gap.

        Domains differ. A system can be well-calibrated on cardiac and badly
        miscalibrated on GI, and a single global offset would smear that into
        uselessness.
        """
        buckets: dict[str, list[Outcome]] = {}

        for o in scored:
            domain = self._domain(o.predicted_condition)
            buckets.setdefault(domain, []).append(o)

        offsets: dict[str, float] = {}

        for domain, items in buckets.items():
            if len(items) < self.MIN_SAMPLES:
                continue
            accuracy = sum(1 for o in items if o.correct) / len(items)
            confidence = statistics.mean(o.predicted_confidence for o in items)
            offsets[domain] = confidence - accuracy

        return offsets

    @staticmethod
    def _domain(condition: str) -> str:
        c = (condition or "").lower()
        table = {
            "gastrointestinal": ("gastr", "colic", "ulcer", "hepat", "gallbladder",
                                 "liver", "bowel", "abdominal", "biliary"),
            "cardiac": ("cardi", "angina", "arrhythm", "infarct", "heart"),
            "respiratory": ("pneumon", "asthma", "bronch", "copd", "respiratory", "lung"),
            "infectious": ("dengue", "malaria", "typhoid", "viral", "bacterial",
                           "infection", "fever"),
            "musculoskeletal": ("muscul", "sprain", "arthr", "joint", "back pain"),
            "neurological": ("migrain", "headache", "neuro", "seizure", "stroke"),
        }
        for domain, keys in table.items():
            if any(k in c for k in keys):
                return domain
        return "other"

    @staticmethod
    def _narrate(report: CalibrationReport) -> str:
        """
        Plain English. The user should be able to read this and know whether to
        trust the thing.
        """
        if report.resolved < 3:
            return (
                "Omni has not made enough predictions for you yet to know how "
                "accurate it is. It will tell you once it does."
            )

        parts: list[str] = [
            f"Across {report.resolved} resolved cases, Omni was right "
            f"{report.correct} times ({report.accuracy:.0%})."
        ]

        gap = report.calibration_gap

        if gap > 0.15:
            parts.append(
                f"It has been consistently overconfident — {gap:.0%} more sure than it "
                "should have been. Confidence on future predictions has been marked down."
            )
        elif gap < -0.15:
            parts.append(
                "It has been more cautious than necessary. Confidence has been marked up."
            )
        else:
            parts.append("Its confidence has been well calibrated.")

        if report.abstentions:
            parts.append(
                f"It declined to answer {report.abstentions} times. "
                f"{report.abstention_precision:.0%} of those were genuinely ambiguous "
                "cases where guessing would have been wrong."
            )

        return " ".join(parts)
