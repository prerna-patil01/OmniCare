import uuid
from datetime import datetime

from extensions import db


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), index=True)

    title = db.Column(db.String(200))
    phase = db.Column(db.String(20), default="probing")  # probing | concluded
    turns_used = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    turns = db.relationship(
        "Turn", backref="conversation", cascade="all, delete-orphan",
        order_by="Turn.created_at", lazy="selectin",
    )

    def to_dict(self, include_turns=True):
        d = {
            "id": self.id,
            "title": self.title,
            "phase": self.phase,
            "turns_used": self.turns_used,
            "created_at": self.created_at.isoformat(),
        }
        if include_turns:
            d["turns"] = [t.to_dict() for t in self.turns]
        return d

    def as_context(self):
        """The shape the ContextBuilder wants."""
        return [{"role": t.role, "content": t.content} for t in self.turns]


class Turn(db.Model):
    __tablename__ = "turns"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(
        db.String(36), db.ForeignKey("conversations.id"), index=True
    )

    role = db.Column(db.String(20))     # user | omni
    content = db.Column(db.Text)

    # When Omni asks, we store WHY — so the UI can show what the question
    # was trying to distinguish between. That transparency is the product.
    discriminates_between = db.Column(db.JSON, default=list)
    why_this_question = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "discriminates_between": self.discriminates_between or [],
            "why_this_question": self.why_this_question,
            "created_at": self.created_at.isoformat(),
        }
