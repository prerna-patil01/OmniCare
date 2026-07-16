"""
The single door to the model.

Every LLM call in OmniCare passes through here. That is deliberate: when
you swap Gemini for something else, or add a fallback, or need to log every
prompt for audit, there is exactly one file to change.

Also handles the thing everyone gets wrong — models return JSON wrapped in
markdown fences roughly half the time, and a naive json.loads() will crash
in front of the judges.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when the model is unreachable or returns something unusable."""


@dataclass
class LLMResponse:
    text: str
    model: str
    latency_ms: int
    raw: Any = None


class LLMClient:
    """
    Thin wrapper over Google Gemini.

    Deliberately not a framework. No chains, no memory abstraction, no
    tool-calling layer. Those hide exactly the reasoning we need to show
    the user, and a Healthcare OS that cannot explain itself is worthless.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self._client = None

        if self.api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self._client = genai
            except ImportError:
                logger.warning("google-generativeai is not installed")

    # ── Public API ────────────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """
        One-shot generation.

        Temperature defaults LOW. This is a clinical system; we are not
        trying to be creative, we are trying to be repeatable. A triage
        score that changes between runs on identical input is not a score,
        it is a random number with a decimal point.
        """
        if not self._client:
            raise LLMError("Gemini is not configured. Set GEMINI_API_KEY before using AI features.")

        started = time.perf_counter()

        try:
            model = self._client.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            result = model.generate_content(prompt)
            elapsed = int((time.perf_counter() - started) * 1000)

            return LLMResponse(
                text=result.text,
                model=self.model_name,
                latency_ms=elapsed,
                raw=result,
            )

        except Exception as exc:  # noqa: BLE001 — we genuinely want any failure here
            logger.exception("LLM call failed")
            raise LLMError(str(exc)) from exc

    def generate_json(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.1,
    ) -> dict:
        """
        Generation that MUST return a dict.

        Temperature is even lower here. Structured output is a parsing task,
        not a writing task.
        """
        response = self.generate(prompt, system=system, temperature=temperature)
        return self.parse_json(response.text)

    # ── Parsing ───────────────────────────────────────────────────

    @staticmethod
    def parse_json(text: str) -> dict:
        """
        Extract a JSON object from model output.

        Models fence their JSON in markdown about half the time, prepend
        "Here is the JSON:" some of the time, and occasionally do both.
        Strip all of it, then find the outermost braces.
        """
        cleaned = text.strip()

        # Strip markdown fences
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        # Find the outermost JSON object — anything before/after is prose
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1 or end < start:
            raise LLMError(f"No JSON object found in model output: {text[:200]}")

        candidate = cleaned[start : end + 1]

        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise LLMError(f"Malformed JSON from model: {exc}") from exc
