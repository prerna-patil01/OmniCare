"""
Persistence adapter for the AI layer.

The Calibrator and PopulationAggregator in ai/ are deliberately storage-agnostic
— they take a `store` and call methods on it. This is that store. Keeping the AI
package free of SQLAlchemy means it can be tested without a database.
"""

from datetime import datetime, timedelta

from ai.calibration import Outcome
from extensions import db
from models import TriageRecord


class TriageStore:
    def save_outcome(self, outcome: Outcome):
        record = TriageRecord.query.get(outcome.triage_id)
        if not record:
            return None

        record.actual_condition = outcome.actual_condition
        record.actual_severity = outcome.actual_severity
        record.confirmed_by = outcome.confirmed_by
        record.confirmed_at = outcome.confirmed_at or datetime.utcnow()
        record.correct = outcome.correct

        db.session.commit()
        return record

    def outcomes_for(self, user_id, since=None):
        q = TriageRecord.query.filter_by(user_id=user_id)
        if since:
            q = q.filter(TriageRecord.created_at >= since)

        return [
            Outcome(
                triage_id=r.id,
                predicted_condition=r.condition or r.clinical_term or "",
                predicted_confidence=r.confidence or 0.0,
                predicted_risk=r.risk_score or 0.0,
                actual_condition=r.actual_condition,
                actual_severity=r.actual_severity,
                confirmed_by=r.confirmed_by,
                confirmed_at=r.confirmed_at,
                correct=r.correct,
                abstained=bool(r.abstained),
            )
            for r in q.all()
        ]

    def triage_records(self, region, since=None, until=None):
        """
        Anonymised records for population aggregation.

        Returns dicts, not ORM objects — a deliberate boundary. Nothing that
        crosses into the population layer carries a user_id.
        """
        q = TriageRecord.query.filter_by(region=region)
        if since:
            q = q.filter(TriageRecord.created_at >= since)
        if until:
            q = q.filter(TriageRecord.created_at < until)

        return [
            {"condition": r.condition, "created_at": r.created_at}
            for r in q.all()
            if r.condition
        ]
