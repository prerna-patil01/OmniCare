"""
Multimodal ingestion. PDF and image → structured biomarkers.

Two paths: pdfplumber for text-native PDFs (fast, exact), and the vision model
for scans and photographs (slower, fallible). We try the cheap one first, because
most Indian lab reports are text-native PDFs and running a vision model over them
is money and latency spent for nothing.
"""

from __future__ import annotations

import base64
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .llm_client import LLMClient
from .prompts import CORE_SYSTEM, REPORT_PARSER

logger = logging.getLogger(__name__)


@dataclass
class ExtractedReport:
    document_type: str = "other"
    report_date: str | None = None
    lab_name: str | None = None

    biomarkers: list[dict] = field(default_factory=list)
    medications: list[dict] = field(default_factory=list)
    impressions: list[str] = field(default_factory=list)

    abnormal_summary: str = ""
    unreadable_sections: list[str] = field(default_factory=list)
    confidence: float = 0.0

    extracted_at: datetime = field(default_factory=datetime.utcnow)
    source: str = "unknown"

    @property
    def abnormal(self) -> list[dict]:
        return [b for b in self.biomarkers if b.get("flag") in ("high", "low", "critical")]

    @property
    def critical(self) -> list[dict]:
        return [b for b in self.biomarkers if b.get("flag") == "critical"]

    @property
    def has_ambiguous_medication(self) -> bool:
        """
        Handwriting is the single most dangerous surface in this entire product.
        Metformin and Metoprolol look nearly identical in a hurried scrawl, and
        they do very different things.
        """
        return any(m.get("legibility") in ("ambiguous", "illegible") for m in self.medications)

    def to_dict(self) -> dict:
        return {
            "document_type": self.document_type,
            "report_date": self.report_date,
            "lab_name": self.lab_name,
            "biomarkers": self.biomarkers,
            "medications": self.medications,
            "impressions": self.impressions,
            "abnormal_summary": self.abnormal_summary,
            "abnormal_count": len(self.abnormal),
            "critical_count": len(self.critical),
            "has_ambiguous_medication": self.has_ambiguous_medication,
            "unreadable_sections": self.unreadable_sections,
            "confidence": round(self.confidence, 2),
            "extracted_at": self.extracted_at.isoformat(),
            "source": self.source,
        }


class ReportExtractor:
    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or LLMClient()

    def extract(self, path: str | Path) -> ExtractedReport:
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(path)

        suffix = path.suffix.lower()

        if suffix == ".pdf":
            text = self._pdf_text(path)
            if text and len(text.strip()) > 100:
                # Text-native PDF. No vision model needed — cheaper, faster, exact.
                return self._from_text(text, source=path.name)
            # Scanned PDF with no text layer. Falls through to vision.
            logger.info("PDF has no usable text layer — falling back to vision")
            return self._from_image(path, source=path.name)

        if suffix in (".png", ".jpg", ".jpeg", ".webp"):
            return self._from_image(path, source=path.name)

        raise ValueError(f"Unsupported file type: {suffix}")

    # ── Text path ─────────────────────────────────────────────────

    @staticmethod
    def _pdf_text(path: Path) -> str:
        try:
            import pdfplumber
        except ImportError:
            logger.warning("pdfplumber not installed — cannot read PDF text layer")
            return ""

        chunks: list[str] = []
        try:
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    chunks.append(page.extract_text() or "")

                    # Lab reports put the numbers in tables. Extracting the text
                    # alone loses the row alignment, which is where the reference
                    # range lives — and without the range, a value means nothing.
                    for table in page.extract_tables() or []:
                        for row in table:
                            cells = [c for c in row if c]
                            if cells:
                                chunks.append(" | ".join(cells))
        except Exception:  # noqa: BLE001
            logger.exception("pdfplumber failed on %s", path)
            return ""

        return "\n".join(chunks)

    def _from_text(self, text: str, source: str) -> ExtractedReport:
        raw = self.llm.generate_json(
            REPORT_PARSER.format(core_system=CORE_SYSTEM, document_text=text[:20000])
        )
        return self._build(raw, source=source)

    # ── Vision path ───────────────────────────────────────────────

    def _from_image(self, path: Path, source: str) -> ExtractedReport:
        if not self.llm._client:  # noqa: SLF001
            logger.warning("No LLM configured — cannot run vision extraction")
            return ExtractedReport(source=source, confidence=0.0)

        try:
            import google.generativeai as genai

            data = base64.b64encode(path.read_bytes()).decode()
            mime = self._mime(path)

            model = genai.GenerativeModel(
                os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
                system_instruction=CORE_SYSTEM,
            )

            result = model.generate_content(
                [
                    REPORT_PARSER.format(
                        core_system=CORE_SYSTEM,
                        document_text="[The document is provided as an image below.]",
                    ),
                    {"mime_type": mime, "data": data},
                ]
            )

            raw = self.llm.parse_json(result.text)
            return self._build(raw, source=source)

        except Exception:  # noqa: BLE001
            logger.exception("Vision extraction failed for %s", path)
            return ExtractedReport(
                source=source,
                confidence=0.0,
                unreadable_sections=["The document could not be read."],
            )

    @staticmethod
    def _mime(path: Path) -> str:
        return {
            ".pdf": "application/pdf",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }.get(path.suffix.lower(), "application/octet-stream")

    # ── Shared ────────────────────────────────────────────────────

    @staticmethod
    def _build(raw: dict, source: str) -> ExtractedReport:
        report = ExtractedReport(
            document_type=raw.get("document_type", "other"),
            report_date=raw.get("report_date"),
            lab_name=raw.get("lab_name"),
            biomarkers=raw.get("biomarkers", []),
            medications=raw.get("medications", []),
            impressions=raw.get("impressions", []),
            abnormal_summary=raw.get("abnormal_summary", ""),
            unreadable_sections=raw.get("unreadable_sections", []),
            confidence=float(raw.get("confidence", 0.0)),
            source=source,
        )

        # A model that says it read an ambiguous prescription clearly is a model
        # that is wrong. Cap the confidence to force a human check.
        if report.has_ambiguous_medication:
            report.confidence = min(report.confidence, 0.5)

        return report
