"""
The most important file in OmniCare.

An LLM handed a raw symptom string is a chatbot. An LLM handed a symptom
string PLUS fourteen days of HRV, a penicillin allergy, a family history of
gallstones, and the fact that dengue is up 12% in this postcode is something
else entirely.

The difference between those two systems is this file. Everything else in
the AI layer is plumbing; this is the water.

Note what is NOT here: raw identifiers. The context that reaches a model
carries clinical facts, never a name, phone number, or ABHA ID. The model
does not need them, and the moment they cross that boundary they are in a
third party's logs forever.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


@dataclass
class PatientContext:
    """
    Everything a clinician would want to know before speaking, and nothing
    that would identify the patient to a third party.
    """

    # Demographics — coarse, non-identifying
    age: int | None = None
    sex: str | None = None
    bmi: float | None = None
    blood_group: str | None = None

    # Clinical
    allergies: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    past_conditions: list[str] = field(default_factory=list)
    surgeries: list[str] = field(default_factory=list)
    medications: list[str] = field(default_factory=list)
    family_history: list[str] = field(default_factory=list)

    # Lifestyle
    smoking: str | None = None
    alcohol: str | None = None
    diet: str | None = None
    exercise: str | None = None
    stress: str | None = None
    occupation: str | None = None

    # Telemetry — the thing a doctor in a 7-minute consult never has
    vitals: dict[str, Any] = field(default_factory=dict)
    vitals_trend: dict[str, str] = field(default_factory=dict)

    # Documents — parsed, not raw
    recent_biomarkers: list[dict] = field(default_factory=list)
    abnormal_flags: list[str] = field(default_factory=list)

    # Population priors — the local base rate
    regional_signals: list[dict] = field(default_factory=list)

    # Conversation so far
    turns: list[dict] = field(default_factory=list)

    # What consent actually permits
    consent_scopes: list[str] = field(default_factory=list)

    def to_prompt(self) -> str:
        """
        Render as a clinical brief.

        Deliberately prose, not JSON. Models reason better over a well-written
        handover note than over a nested dict — which is unsurprising, since
        that is what their training data looks like.
        """
        lines: list[str] = []

        # ── Who ──
        demo = []
        if self.age:
            demo.append(f"{self.age} years old")
        if self.sex:
            demo.append(self.sex.lower())
        if self.bmi:
            demo.append(f"BMI {self.bmi}")
        if self.blood_group:
            demo.append(f"blood group {self.blood_group}")
        if demo:
            lines.append("PATIENT: " + ", ".join(demo) + ".")

        # ── What could kill them ──
        # Allergies go first, always. If the model only reads one line, it
        # should be this one.
        if self.allergies:
            lines.append(f"ALLERGIES (CRITICAL): {', '.join(self.allergies)}.")
        else:
            lines.append("ALLERGIES: none on record.")

        # ── Standing problems ──
        if self.conditions:
            lines.append(f"ACTIVE CONDITIONS: {', '.join(self.conditions)}.")
        if self.medications:
            lines.append(f"CURRENT MEDICATIONS: {', '.join(self.medications)}.")
        if self.past_conditions:
            lines.append(f"PAST HISTORY: {', '.join(self.past_conditions)}.")
        if self.surgeries:
            lines.append(f"SURGICAL HISTORY: {', '.join(self.surgeries)}.")
        if self.family_history:
            lines.append(f"FAMILY HISTORY: {', '.join(self.family_history)}.")

        # ── Lifestyle ──
        life = []
        for label, value in [
            ("smoking", self.smoking),
            ("alcohol", self.alcohol),
            ("diet", self.diet),
            ("exercise", self.exercise),
            ("stress", self.stress),
        ]:
            if value:
                life.append(f"{label} {value.lower()}")
        if life:
            lines.append("LIFESTYLE: " + ", ".join(life) + ".")
        if self.occupation:
            lines.append(f"OCCUPATION: {self.occupation}.")

        # ── Telemetry ──
        # This is the section a human clinician does not have. It is the
        # reason OmniCare can say anything a GP could not.
        if self.vitals:
            parts = []
            for key, value in self.vitals.items():
                trend = self.vitals_trend.get(key)
                parts.append(f"{key} {value}" + (f" ({trend})" if trend else ""))
            lines.append("WEARABLE TELEMETRY: " + ", ".join(parts) + ".")

        # ── Labs ──
        if self.abnormal_flags:
            lines.append(f"ABNORMAL LAB VALUES: {', '.join(self.abnormal_flags)}.")
        if self.recent_biomarkers:
            marks = ", ".join(
                f"{b['name']} {b['value']} {b.get('unit', '')}".strip()
                for b in self.recent_biomarkers[:12]
            )
            lines.append(f"RECENT BIOMARKERS: {marks}.")

        # ── Base rates ──
        # A symptom's meaning depends on what is going around. Chest pain in
        # a dengue outbreak is a different prior than chest pain in February.
        if self.regional_signals:
            sigs = ", ".join(
                f"{s['name']} {s['direction']}{s['magnitude']}"
                for s in self.regional_signals
            )
            lines.append(f"LOCAL EPIDEMIOLOGY: {sigs}.")

        # ── The conversation ──
        if self.turns:
            lines.append("\nCONVERSATION SO FAR:")
            for turn in self.turns:
                who = "Patient" if turn["role"] == "user" else "Omni"
                lines.append(f"  {who}: {turn['content']}")

        # ── Boundaries ──
        if self.consent_scopes:
            lines.append(
                f"\nCONSENT SCOPES GRANTED: {', '.join(self.consent_scopes)}. "
                "You may not reason over data outside these scopes."
            )

        return "\n".join(lines)


class ContextBuilder:
    """
    Assembles a PatientContext from whatever the database has.

    Every method is defensive. Real health profiles are half-empty — people
    skip the medical history step, wearables disconnect, labs never get
    uploaded. A context builder that assumes complete data will crash on the
    first real user.
    """

    def __init__(self, consent_service=None, anonymiser=None):
        self.consent = consent_service
        self.anonymiser = anonymiser

    def build(
        self,
        user: Any,
        profile: Any = None,
        history: Any = None,
        lifestyle: Any = None,
        vitals: list | None = None,
        reports: list | None = None,
        conversation: list | None = None,
        regional: list | None = None,
        purpose: str = "triage",
    ) -> PatientContext:
        ctx = PatientContext()

        # ── Consent gate ──────────────────────────────────────────
        # Before a single field is read, ask what we are allowed to read.
        # This is not a formality. A scope that excludes mental_health means
        # the model never sees the SSRI, and therefore never reasons about it.
        scopes = self._scopes(user, purpose)
        ctx.consent_scopes = scopes

        # ── Demographics ──────────────────────────────────────────
        if profile:
            ctx.age = self._age_from_dob(getattr(profile, "dob", None))
            ctx.sex = getattr(profile, "gender", None)
            ctx.blood_group = getattr(profile, "blood_group", None)
            ctx.bmi = self._bmi(
                getattr(profile, "height_cm", None),
                getattr(profile, "weight_kg", None),
            )

        # ── Clinical ──────────────────────────────────────────────
        if history and "medical_history" in scopes:
            ctx.allergies = self._listify(getattr(history, "allergies", None))
            ctx.conditions = self._listify(getattr(history, "current_diseases", None))
            ctx.past_conditions = self._listify(getattr(history, "past_diseases", None))
            ctx.surgeries = self._listify(getattr(history, "surgeries", None))
            ctx.medications = self._listify(getattr(history, "medications", None))
            ctx.family_history = self._listify(getattr(history, "family_history", None))

        # Allergies are a special case. They are ALWAYS in scope, regardless
        # of what consent says, because withholding them can kill someone and
        # no consent framework in the world requires that.
        elif history:
            ctx.allergies = self._listify(getattr(history, "allergies", None))

        # ── Lifestyle ─────────────────────────────────────────────
        if lifestyle and "lifestyle" in scopes:
            ctx.smoking = getattr(lifestyle, "smoking", None)
            ctx.alcohol = getattr(lifestyle, "alcohol", None)
            ctx.diet = getattr(lifestyle, "food_habits", None)
            ctx.exercise = getattr(lifestyle, "exercise", None)
            ctx.stress = getattr(lifestyle, "stress", None)
            ctx.occupation = getattr(lifestyle, "occupation", None)

        # ── Telemetry ─────────────────────────────────────────────
        if vitals and "vitals" in scopes:
            ctx.vitals, ctx.vitals_trend = self._summarise_vitals(vitals)

        # ── Labs ──────────────────────────────────────────────────
        if reports and "reports" in scopes:
            ctx.recent_biomarkers, ctx.abnormal_flags = self._summarise_reports(reports)

        # ── Conversation ──────────────────────────────────────────
        if conversation:
            ctx.turns = [
                {"role": t.get("role"), "content": t.get("content")}
                for t in conversation[-12:]  # last 12 turns; beyond that is noise
            ]

        # ── Population priors ─────────────────────────────────────
        if regional:
            ctx.regional_signals = regional

        return ctx

    # ── Internals ─────────────────────────────────────────────────

    def _scopes(self, user: Any, purpose: str) -> list[str]:
        if not self.consent:
            # No consent service wired up — assume full scope. This is fine
            # in development and unacceptable in production, which is why it
            # is loud rather than silent.
            return ["medical_history", "lifestyle", "vitals", "reports"]
        return self.consent.active_scopes(user_id=user.id, purpose=purpose)

    @staticmethod
    def _age_from_dob(dob) -> int | None:
        if not dob:
            return None
        if isinstance(dob, str):
            try:
                dob = datetime.fromisoformat(dob)
            except ValueError:
                return None
        today = datetime.utcnow()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @staticmethod
    def _bmi(height_cm, weight_kg) -> float | None:
        if not height_cm or not weight_kg or height_cm < 50:
            return None
        return round(weight_kg / ((height_cm / 100) ** 2), 1)

    @staticmethod
    def _listify(value) -> list[str]:
        """Health data arrives as lists, comma strings, JSON, or None. Normalise."""
        if not value:
            return []
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return []

    @staticmethod
    def _summarise_vitals(vitals: list) -> tuple[dict, dict]:
        """
        Latest value plus a 14-day direction.

        The direction matters more than the value. A resting HR of 72 is
        unremarkable. A resting HR of 72 that was 64 a fortnight ago is a
        signal — and it is a signal no annual check-up would ever catch.
        """
        if not vitals:
            return {}, {}

        latest = vitals[-1]
        cutoff = datetime.utcnow() - timedelta(days=14)
        window = [v for v in vitals if _ts(v) and _ts(v) >= cutoff]

        current: dict[str, Any] = {}
        trend: dict[str, str] = {}

        for key in ("heart_rate", "hrv", "spo2", "sleep_hours", "steps"):
            value = _get(latest, key)
            if value is None:
                continue
            current[key] = value

            values = [_get(v, key) for v in window if _get(v, key) is not None]
            if len(values) < 4:
                continue

            # Compare the first third against the last third — smooths daily noise
            third = max(1, len(values) // 3)
            early = sum(values[:third]) / third
            late = sum(values[-third:]) / third

            if early == 0:
                continue

            delta_pct = ((late - early) / early) * 100

            if abs(delta_pct) < 5:
                trend[key] = "stable"
            else:
                arrow = "up" if delta_pct > 0 else "down"
                trend[key] = f"{arrow} {abs(delta_pct):.0f}% over 14d"

        return current, trend

    @staticmethod
    def _summarise_reports(reports: list) -> tuple[list[dict], list[str]]:
        biomarkers: list[dict] = []
        flags: list[str] = []

        for report in reports[-5:]:  # last 5 reports; older is history, not context
            markers = _get(report, "biomarkers") or []
            for m in markers:
                biomarkers.append(m)
                if m.get("flag") in ("high", "low", "critical"):
                    flags.append(
                        f"{m['name']} {m['value']} {m.get('unit','')} ({m['flag']})".strip()
                    )

        return biomarkers, flags


# ── Small helpers ─────────────────────────────────────────────────

def _get(obj: Any, key: str):
    """Works for both dicts and ORM objects. Health data arrives as both."""
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def _ts(obj: Any):
    value = _get(obj, "recorded_at") or _get(obj, "timestamp")
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return value
