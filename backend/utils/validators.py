"""Lightweight validation. No framework — a hackathon does not need Marshmallow."""

import re

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$")
PHONE_RE = re.compile(r"^\d{10}$")
ABHA_RE = re.compile(r"^\d{2}-?\d{4}-?\d{4}-?\d{4}$")


def is_email(value: str) -> bool:
    return bool(value and EMAIL_RE.match(value))


def is_phone(value: str) -> bool:
    return bool(value and PHONE_RE.match(value))


def is_abha(value: str) -> bool:
    return bool(value and ABHA_RE.match(value))


def require_fields(data: dict, *fields):
    """
    Return the list of missing fields.

    Caller decides what to do — validation reports, it does not raise. A
    validator that raises forces try/except at every call site.
    """
    return [f for f in fields if not data.get(f)]


def clamp(value, lo, hi):
    return max(lo, min(hi, value))
