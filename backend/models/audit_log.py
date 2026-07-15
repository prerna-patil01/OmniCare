"""
Immutable audit trail.

Append-only. Nothing in this application updates or deletes an AuditEntry, and
that is not an oversight — an audit log you can edit is not an audit log.

Every consent check is recorded. Not just the denials. When a patient asks "who
looked at my liver panel and when," the answer must be complete, and you cannot
reconstruct a complete answer from a log that only recorded the failures.
"""

import uuid
from datetime import datetime

from extensions import db


class AuditEntry(db.Model):
    __tablename__ = "audit_entries"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), index=True)

    actor = db.Column(db.String(120))       # agent:triage | doctor:menon | system
    action = db.Column(db.String(60))       # consent_check | data_read | data_share
    scope = db.Column(db.String(60))

    granted = db.Column(db.Boolean)
    reason = db.Column(db.String(400))

    at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "actor": self.actor,
            "action": self.action,
            "scope": self.scope,
            "granted": self.granted,
            "reason": self.reason,
            "at": self.at.isoformat(),
        }
