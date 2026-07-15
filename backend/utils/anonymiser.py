"""
Strips identity before anything reaches Layer 4 or a third-party model.

The rule: a model may know that a 21-year-old woman has right upper quadrant
pain. It may never know her name, her phone number, or her ABHA ID. Those add
nothing clinically and everything legally.
"""

import hashlib
import re


class Anonymiser:
    # Direct identifiers. These never leave the database.
    STRIP_FIELDS = {
        "name", "email", "phone", "abha_id", "address",
        "emergency_contact", "aadhaar", "pan",
    }

    # Free-text patterns that leak identity even when the field name doesn't.
    PATTERNS = [
        (re.compile(r"\b\d{10}\b"), "[PHONE]"),
        (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"), "[EMAIL]"),
        (re.compile(r"\b\d{2}-\d{4}-\d{4}-\d{4}\b"), "[ABHA]"),
        (re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"), "[AADHAAR]"),
    ]

    @classmethod
    def scrub_dict(cls, data: dict) -> dict:
        return {
            k: cls.scrub_text(v) if isinstance(v, str) else v
            for k, v in data.items()
            if k not in cls.STRIP_FIELDS
        }

    @classmethod
    def scrub_text(cls, text: str) -> str:
        for pattern, replacement in cls.PATTERNS:
            text = pattern.sub(replacement, text)
        return text

    @staticmethod
    def pseudonym(user_id: str, salt: str = "omnicare") -> str:
        """
        Stable pseudonym for population aggregation.

        Lets us count "this person appears in the dengue cohort" without ever
        knowing who they are. Hashing is not anonymisation on its own — but
        combined with the k-anonymity threshold in population_agg, it's honest.
        """
        return hashlib.sha256(f"{salt}:{user_id}".encode()).hexdigest()[:16]
