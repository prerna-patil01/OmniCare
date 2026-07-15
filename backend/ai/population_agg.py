"""
Layer 4 — Population Intelligence.

Aggregates anonymised symptoms into regional signals, and — crucially — feeds
them BACK DOWN into individual triage via the Population Agent.

That downward flow is the point. Every health app has an outbreak map. It sits
there, looking impressive, changing nobody's diagnosis. Here, "dengue is up 12%
in this postcode" actually shifts the differential for the patient in front of
you, because the Population Agent carries it into the deliberation.

That is what closes the four-layer architecture. Without it, Layer 4 is a poster.
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class RegionalSignal:
    name: str
    magnitude: float
    direction: str              # "up" | "down" | "flat"
    baseline: float
    current: float
    confidence: float
    case_count: int
    region: str
    window_days: int = 7

    @property
    def significant(self) -> bool:
        """
        Two conditions, both required.

        A 40% rise built on 3 cases is noise. A 2% rise on 10,000 cases is a
        rounding error. Neither should reach a patient.
        """
        return abs(self.magnitude) >= 10.0 and self.case_count >= 8

    def to_context(self) -> dict:
        return {
            "name": self.name,
            "direction": self.direction,
            "magnitude": f"{abs(self.magnitude):.0f}%",
            "cases": self.case_count,
            "region": self.region,
        }

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "magnitude": round(self.magnitude, 1),
            "direction": self.direction,
            "baseline": round(self.baseline, 2),
            "current": round(self.current, 2),
            "confidence": round(self.confidence, 2),
            "case_count": self.case_count,
            "region": self.region,
            "significant": self.significant,
        }


class PopulationAggregator:
    """
    Turns individual triage records into regional epidemiology.

    Every record entering this class has already passed through the anonymiser.
    Nothing here should be able to identify anyone, and if it can, that is a bug
    of the most serious kind.

    K-anonymity threshold of 8: we do not report a signal built on fewer than 8
    cases, because in a small enough region, "3 dengue cases" plus a postcode is
    a name.
    """

    K_ANONYMITY = 8

    def __init__(self, store=None, anonymiser=None):
        self.store = store
        self.anonymiser = anonymiser

    def signals_for(self, region: str, window_days: int = 7) -> list[RegionalSignal]:
        if not self.store:
            return []

        now = datetime.utcnow()
        current_window = now - timedelta(days=window_days)
        baseline_window = now - timedelta(days=window_days * 6)  # ~6 weeks back

        recent = self.store.triage_records(
            region=region, since=current_window
        )
        baseline = self.store.triage_records(
            region=region, since=baseline_window, until=current_window
        )

        if len(recent) < self.K_ANONYMITY:
            # Not enough people. Reporting anyway would be both statistically
            # meaningless and a privacy violation.
            logger.info("Region %s below k-anonymity threshold", region)
            return []

        recent_counts = Counter(self._condition(r) for r in recent)
        baseline_counts = Counter(self._condition(r) for r in baseline)

        # Normalise to rate-per-case, so a busy week does not look like an outbreak
        recent_total = max(1, len(recent))
        baseline_total = max(1, len(baseline))

        signals: list[RegionalSignal] = []

        for condition, count in recent_counts.items():
            if condition == "unknown" or count < self.K_ANONYMITY:
                continue

            current_rate = count / recent_total
            baseline_rate = baseline_counts.get(condition, 0) / baseline_total

            if baseline_rate == 0:
                # Something new. Treat as a rise, but with low confidence — a
                # condition with no baseline could equally be a coding change.
                magnitude = 100.0
                confidence = 0.4
            else:
                magnitude = ((current_rate - baseline_rate) / baseline_rate) * 100
                # Confidence scales with sample size, and caps out. More data
                # cannot make you certain; it can only make you less uncertain.
                confidence = min(0.9, 0.3 + (count / 100))

            direction = "up" if magnitude > 2 else "down" if magnitude < -2 else "flat"

            signals.append(
                RegionalSignal(
                    name=condition,
                    magnitude=magnitude,
                    direction=direction,
                    baseline=baseline_rate,
                    current=current_rate,
                    confidence=confidence,
                    case_count=count,
                    region=region,
                    window_days=window_days,
                )
            )

        # Only the significant ones reach a patient. Loudest first.
        return sorted(
            [s for s in signals if s.significant],
            key=lambda s: abs(s.magnitude),
            reverse=True,
        )

    def context_for(self, region: str) -> list[dict]:
        """
        The shape the ContextBuilder wants.

        This is the wire from Layer 4 back down to Layer 2. It is three lines
        long, and it is the reason the architecture is a system rather than a
        stack of features.
        """
        return [s.to_context() for s in self.signals_for(region)[:5]]

    @staticmethod
    def _condition(record) -> str:
        if isinstance(record, dict):
            return (record.get("condition") or "unknown").lower()
        return (getattr(record, "condition", None) or "unknown").lower()
