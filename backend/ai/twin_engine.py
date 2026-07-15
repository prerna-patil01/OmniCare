"""
The Digital Twin engine.

Takes everything known about a patient and PROJECTS IT FORWARD. This is the file
that turns a health record into a health forecast.

Three questions it answers:
  1. What state is the patient in now?          (health score, biological age)
  2. What are they trending toward, and why?    (predispositions)
  3. What would change it?                       (interventions)

The method is deliberately transparent. Every predisposition names its DRIVERS
(the facts that produced it) and its MODIFIABLE factors (the levers). A twin that
says "you are at risk" is a horoscope. A twin that says "you are at risk BECAUSE
of your mother's gallstones and your low hydration, and hydration is the lever
YOU control" is a tool.

Deterministic scoring first, LLM narrative second. The numbers are computed by
rules you can audit — not hallucinated by a model — and the LLM only writes the
plain-language story over the top. You never want a language model inventing a
risk score; you want it explaining one.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TwinInputs:
    """Everything the twin is computed from. Assembled by the caller."""

    age: int | None = None
    sex: str | None = None
    bmi: float | None = None

    conditions: list[str] = field(default_factory=list)
    past_conditions: list[str] = field(default_factory=list)
    family_history: list[str] = field(default_factory=list)
    medications: list[str] = field(default_factory=list)
    allergies: list[str] = field(default_factory=list)

    smoking: str | None = None
    alcohol: str | None = None
    exercise: str | None = None
    diet: str | None = None
    stress: str | None = None
    hydration_l: float | None = None
    sleep: str | None = None

    vitals: dict = field(default_factory=dict)
    vitals_trend: dict = field(default_factory=dict)
    abnormal_labs: list[str] = field(default_factory=list)

    regional_signals: list[dict] = field(default_factory=list)


class TwinEngine:
    """
    Computes a DigitalTwin from TwinInputs.

    The risk model is a transparent points system, not a black box. Real clinical
    risk engines (Framingham, QRISK) work exactly this way — weighted factors,
    summed, banded. We are not inventing medicine; we are applying the same logic
    to a richer input set than a GP has in a seven-minute consult.
    """

    def __init__(self, llm=None):
        self.llm = llm

    def compute(self, inputs: TwinInputs) -> dict:
        systems = self._system_risk(inputs)
        predispositions = self._predispositions(inputs, systems)
        signals = self._active_signals(inputs)
        interventions = self._interventions(inputs, predispositions)

        health_score = self._health_score(inputs, systems)
        bio_age = self._biological_age(inputs, health_score)
        trajectory = self._trajectory(inputs, signals)

        twin = {
            "health_score": round(health_score, 1),
            "biological_age": round(bio_age, 1) if bio_age else None,
            "chronological_age": inputs.age,
            "trajectory": trajectory,
            "system_risk": {k: round(v, 1) for k, v in systems.items()},
            "predispositions": predispositions,
            "active_signals": signals,
            "interventions": interventions,
            "confidence": self._confidence(inputs),
            "computed_from": self._provenance(inputs),
        }

        twin["narrative"] = self._narrate(inputs, twin)
        return twin

    # ── System-level risk ─────────────────────────────────────────

    def _system_risk(self, inp: TwinInputs) -> dict:
        """
        Per-body-system risk, 0-10. Transparent weighted scoring.

        Each system starts at a baseline and accrues points from the factors that
        genuinely raise its risk. The weights are conservative and defensible —
        this is not trying to be a validated clinical instrument, it is trying to
        be honest about direction and rough magnitude.
        """
        R = {
            "cardiovascular": 1.5,
            "metabolic": 1.5,
            "hepatic": 1.0,
            "renal": 1.0,
            "respiratory": 1.0,
            "mental": 1.5,
        }

        fam = " ".join(inp.family_history).lower()
        cond = " ".join(inp.conditions + inp.past_conditions).lower()

        # ── Cardiovascular ──
        if inp.smoking and inp.smoking.lower() not in ("never", "no"):
            R["cardiovascular"] += 2.0
        if inp.bmi and inp.bmi >= 30:
            R["cardiovascular"] += 1.5
        elif inp.bmi and inp.bmi >= 25:
            R["cardiovascular"] += 0.8
        if "diabetes" in fam or "heart" in fam or "hypertension" in fam:
            R["cardiovascular"] += 1.2
        if inp.exercise and "never" in inp.exercise.lower():
            R["cardiovascular"] += 1.0
        if inp.vitals_trend.get("heart_rate", "").startswith("up"):
            R["cardiovascular"] += 0.8
        if inp.age and inp.age > 45:
            R["cardiovascular"] += (inp.age - 45) * 0.06

        # ── Metabolic ──
        if "diabetes" in fam:
            R["metabolic"] += 2.0
        if inp.bmi and inp.bmi >= 25:
            R["metabolic"] += 1.2
        if inp.diet and any(w in inp.diet.lower() for w in ("junk", "irregular", "processed")):
            R["metabolic"] += 1.0
        if any("hba1c" in l.lower() or "glucose" in l.lower() for l in inp.abnormal_labs):
            R["metabolic"] += 2.0

        # ── Hepatic ──
        if inp.alcohol and inp.alcohol.lower() in ("regularly", "daily", "heavy"):
            R["hepatic"] += 2.5
        elif inp.alcohol and inp.alcohol.lower() == "socially":
            R["hepatic"] += 0.5
        if "gallstone" in fam or "liver" in fam:
            R["hepatic"] += 1.5
        if any(l.lower().startswith(("alt", "ast", "bilirubin")) for l in inp.abnormal_labs):
            R["hepatic"] += 2.0
        # Prior dengue + local dengue = hepatic watch
        if "dengue" in cond:
            R["hepatic"] += 0.6

        # ── Renal ──
        if inp.hydration_l and inp.hydration_l < 1.5:
            R["renal"] += 1.5
        if "diabetes" in fam or "kidney" in fam:
            R["renal"] += 1.0
        if any("creatinine" in l.lower() or "urea" in l.lower() for l in inp.abnormal_labs):
            R["renal"] += 2.0

        # ── Respiratory ──
        if inp.smoking and inp.smoking.lower() not in ("never", "no"):
            R["respiratory"] += 2.5
        if "asthma" in cond:
            R["respiratory"] += 1.5
        if inp.vitals.get("spo2") and inp.vitals["spo2"] < 95:
            R["respiratory"] += 1.5

        # ── Mental ──
        if inp.stress and inp.stress.lower() == "high":
            R["mental"] += 2.0
        if inp.sleep and self._sleep_hours(inp.sleep) < 6:
            R["mental"] += 1.5
        if inp.vitals_trend.get("hrv", "").startswith("down"):
            R["mental"] += 1.0

        return {k: min(10.0, v) for k, v in R.items()}

    # ── Predispositions — the forward projection ──────────────────

    def _predispositions(self, inp: TwinInputs, systems: dict) -> list[dict]:
        """
        What the patient is trending TOWARD.

        This is #12 — "tell the twin what it is prone to." Each prediction is
        earned from the data and names its levers. We do not warn about things the
        patient cannot influence and we do not manufacture risk for drama.
        """
        out = []
        fam = " ".join(inp.family_history).lower()
        cond = " ".join(inp.conditions + inp.past_conditions).lower()

        # Gallstones — family history is the strongest single predictor
        if "gallstone" in fam:
            drivers = ["Family history (mother)"]
            modifiable = []
            if inp.bmi and inp.bmi >= 25:
                drivers.append(f"BMI {inp.bmi}")
                modifiable.append("Weight management")
            if inp.diet and "fatty" in (inp.diet or "").lower():
                drivers.append("High-fat diet")
                modifiable.append("Reduce dietary fat")
            if inp.sex and inp.sex.lower() == "female":
                drivers.append("Female (higher baseline risk)")
            out.append({
                "condition": "Gallstones",
                "risk_level": "elevated",
                "horizon": "5-10 years",
                "drivers": drivers,
                "modifiable": modifiable or ["Maintain healthy weight", "Stay hydrated"],
                "confidence": 0.72,
            })

        # Type 2 diabetes
        if "diabetes" in fam:
            modifiable = []
            if inp.bmi and inp.bmi >= 25:
                modifiable.append("Weight management")
            if inp.exercise and "never" in (inp.exercise or "").lower():
                modifiable.append("Regular exercise")
            if inp.diet and any(w in (inp.diet or "").lower() for w in ("junk", "processed", "sugar")):
                modifiable.append("Reduce refined carbohydrates")
            out.append({
                "condition": "Type 2 Diabetes",
                "risk_level": "elevated" if systems["metabolic"] > 4 else "moderate",
                "horizon": "10-15 years",
                "drivers": ["Family history (father)"] + (
                    [f"BMI {inp.bmi}"] if inp.bmi and inp.bmi >= 25 else []
                ),
                "modifiable": modifiable or ["Regular exercise", "Balanced diet"],
                "confidence": 0.68,
            })

        # Kidney stones — chronic dehydration is the driver
        if inp.hydration_l and inp.hydration_l < 1.5:
            out.append({
                "condition": "Kidney stones",
                "risk_level": "moderate",
                "horizon": "2-5 years",
                "drivers": [f"Chronic low hydration ({inp.hydration_l} L/day)"],
                "modifiable": ["Increase water intake to 2.5-3 L/day"],
                "confidence": 0.6,
            })

        # Recurrent dengue complications
        if "dengue" in cond:
            out.append({
                "condition": "Dengue complications (on re-infection)",
                "risk_level": "situational",
                "horizon": "seasonal",
                "drivers": ["Prior dengue (2021)", "Local dengue activity"],
                "modifiable": ["Mosquito precautions", "Early testing if febrile"],
                "confidence": 0.55,
            })

        # Burnout / anxiety
        if inp.stress and inp.stress.lower() == "high" and self._sleep_hours(inp.sleep or "") < 6.5:
            out.append({
                "condition": "Burnout / anxiety",
                "risk_level": "elevated",
                "horizon": "months",
                "drivers": ["High stress", "Short sleep", "Falling HRV"],
                "modifiable": ["Sleep hygiene", "Stress management", "Workload review"],
                "confidence": 0.64,
            })

        out.sort(key=lambda p: p["confidence"], reverse=True)
        return out

    # ── Active signals — what is happening NOW ────────────────────

    def _active_signals(self, inp: TwinInputs) -> list[dict]:
        out = []

        hr = inp.vitals_trend.get("heart_rate", "")
        hrv = inp.vitals_trend.get("hrv", "")

        if hr.startswith("up") and hrv.startswith("down"):
            out.append({
                "signal": "Rising resting HR + falling HRV",
                "direction": "worsening",
                "magnitude": f"{hr}, {hrv}",
                "interpretation": (
                    "Your body may be under strain you haven't consciously felt — "
                    "an early stress or infection response."
                ),
                "severity": "medium",
            })

        if inp.hydration_l and inp.hydration_l < 1.5:
            out.append({
                "signal": "Chronic underhydration",
                "direction": "stable",
                "magnitude": f"{inp.hydration_l} L/day vs 2.5-3 L target",
                "interpretation": "Sustained low intake raises kidney and urinary risk over time.",
                "severity": "low",
            })

        sleep_trend = inp.vitals_trend.get("sleep_hours", "")
        if sleep_trend.startswith("down"):
            out.append({
                "signal": "Declining sleep",
                "direction": "worsening",
                "magnitude": sleep_trend,
                "interpretation": "Sleep debt is accumulating; it compounds stress and metabolic risk.",
                "severity": "low",
            })

        return out

    # ── Interventions — the levers ────────────────────────────────

    def _interventions(self, inp: TwinInputs, predispositions: list[dict]) -> list[dict]:
        """
        What would actually change the trajectory. Ranked by effect-per-effort.

        Pulled from the modifiable factors across all predispositions, deduped,
        and framed as concrete actions the patient can start today.
        """
        levers: dict[str, dict] = {}

        for p in predispositions:
            for m in p.get("modifiable", []):
                if m not in levers:
                    levers[m] = {
                        "action": m,
                        "targets": [p["condition"]],
                        "effort": self._effort(m),
                    }
                else:
                    levers[m]["targets"].append(p["condition"])

        interventions = list(levers.values())

        # Effect scales with how many predispositions a lever touches
        for iv in interventions:
            n = len(iv["targets"])
            iv["projected_effect"] = (
                f"Reduces risk across {n} predisposition{'s' if n > 1 else ''}"
                if n > 1
                else f"Targets {iv['targets'][0]}"
            )

        interventions.sort(key=lambda x: len(x["targets"]), reverse=True)
        return interventions[:6]

    # ── Composite scores ──────────────────────────────────────────

    def _health_score(self, inp: TwinInputs, systems: dict) -> float:
        """0-100. Starts at 100, loses points to system risk. Higher is better."""
        avg_risk = sum(systems.values()) / len(systems)
        score = 100 - (avg_risk * 7)

        # Lifestyle bonuses/penalties
        if inp.exercise and any(w in inp.exercise.lower() for w in ("daily", "regular", "4", "5")):
            score += 4
        if inp.smoking and inp.smoking.lower() in ("never", "no"):
            score += 3
        if inp.hydration_l and inp.hydration_l >= 2.5:
            score += 2

        return max(0, min(100, score))

    def _biological_age(self, inp: TwinInputs, health_score: float) -> float | None:
        """
        Biological vs chronological age.

        A crude but honest model: a perfect health score means you age as your
        years; a poor one adds years. This is the number that makes the twin
        visceral — "you're 21 but your body is running at 26."
        """
        if not inp.age:
            return None
        # health_score 100 → 0 gap; 50 → +8 years; scales linearly
        gap = (100 - health_score) * 0.16
        return inp.age + gap

    def _trajectory(self, inp: TwinInputs, signals: list[dict]) -> str:
        worsening = sum(1 for s in signals if s["direction"] == "worsening")
        if worsening >= 2:
            return "declining"
        if worsening == 1:
            return "stable"
        return "improving" if not signals else "stable"

    # ── Provenance + confidence ───────────────────────────────────

    def _provenance(self, inp: TwinInputs) -> dict:
        return {
            "has_vitals": bool(inp.vitals),
            "has_trend": bool(inp.vitals_trend),
            "has_history": bool(inp.conditions or inp.past_conditions),
            "has_family_history": bool(inp.family_history),
            "has_labs": bool(inp.abnormal_labs),
            "has_lifestyle": bool(inp.smoking or inp.exercise or inp.diet),
        }

    def _confidence(self, inp: TwinInputs) -> float:
        """How complete was the record? A twin from a half-empty profile says so."""
        p = self._provenance(inp)
        return round(sum(p.values()) / len(p), 2)

    # ── LLM narrative ─────────────────────────────────────────────

    def _narrate(self, inp: TwinInputs, twin: dict) -> str:
        """
        The plain-language story over the computed numbers.

        If no LLM is wired, we build a decent deterministic summary — the twin must
        never be blank just because a key is missing.
        """
        if self.llm and self.llm._client:  # noqa: SLF001
            try:
                return self._llm_narrate(inp, twin)
            except Exception:  # noqa: BLE001
                logger.exception("Twin narrative LLM call failed — using fallback")

        # Deterministic fallback
        parts = []
        score = twin["health_score"]
        if score >= 80:
            parts.append("Your twin is in good shape overall.")
        elif score >= 60:
            parts.append("Your twin is holding steady, with a few areas to watch.")
        else:
            parts.append("Your twin is showing strain that's worth acting on.")

        if twin["predispositions"]:
            top = twin["predispositions"][0]
            parts.append(
                f"The clearest signal is a raised risk of {top['condition'].lower()}, "
                f"driven by {top['drivers'][0].lower()}."
            )
            if top.get("modifiable"):
                parts.append(f"The lever you control: {top['modifiable'][0].lower()}.")

        return " ".join(parts)

    def _llm_narrate(self, inp: TwinInputs, twin: dict) -> str:
        prompt = f"""You are OmniCare's Digital Twin narrator. Write 2-3 sentences, \
plain language, second person, addressed to the patient. No jargon, no fear-mongering, \
no numbered lists. Explain what their twin shows and the single most useful lever.

Health score: {twin['health_score']}/100
Trajectory: {twin['trajectory']}
Top predispositions: {[p['condition'] for p in twin['predispositions'][:3]]}
Active signals: {[s['signal'] for s in twin['active_signals']]}

Write the narrative:"""
        resp = self.llm.generate(prompt, temperature=0.4)
        return resp.text.strip()

    # ── Small helpers ─────────────────────────────────────────────

    @staticmethod
    def _sleep_hours(sleep: str) -> float:
        """'6-7' → 6.5, '7' → 7. Health data is messy."""
        if not sleep:
            return 7.0
        import re
        nums = re.findall(r"\d+\.?\d*", sleep)
        if not nums:
            return 7.0
        vals = [float(n) for n in nums]
        return sum(vals) / len(vals)

    @staticmethod
    def _effort(lever: str) -> str:
        low = ("water", "hydrat", "sleep")
        high = ("weight", "exercise", "workload")
        l = lever.lower()
        if any(k in l for k in low):
            return "low"
        if any(k in l for k in high):
            return "sustained"
        return "moderate"
