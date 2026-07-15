"""Report ingestion. PDF and image → structured biomarkers → pinned to an organ."""

import os
import uuid

from flask import Blueprint, current_app, request
from werkzeug.utils import secure_filename

from ai import LLMClient, ReportExtractor
from extensions import db
from models import Finding, Report
from utils import current_user, ok, error, require_auth

report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

_extractor = ReportExtractor(llm=LLMClient())


@report_bp.post("/upload")
@require_auth
def upload():
    user = current_user()

    if "file" not in request.files:
        return error("No file supplied.")

    file = request.files["file"]
    if not file.filename:
        return error("No file selected.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
        return error(f"Cannot read '{ext}' files. Try PDF, PNG or JPG.")

    upload_dir = current_app.config["UPLOAD_DIR"]
    os.makedirs(upload_dir, exist_ok=True)

    safe = secure_filename(file.filename)
    stored = os.path.join(upload_dir, f"{uuid.uuid4().hex}_{safe}")
    file.save(stored)

    try:
        extracted = _extractor.extract(stored)
    except Exception as exc:  # noqa: BLE001
        current_app.logger.exception("Extraction failed")
        return error(f"Could not read that document: {exc}", 422)

    report = Report(
        user_id=user.id,
        filename=safe,
        stored_path=stored,
        document_type=extracted.document_type,
        report_date=extracted.report_date,
        lab_name=extracted.lab_name,
        biomarkers=extracted.biomarkers,
        medications=extracted.medications,
        impressions=extracted.impressions,
        abnormal_summary=extracted.abnormal_summary,
        unreadable_sections=extracted.unreadable_sections,
        has_ambiguous_medication=extracted.has_ambiguous_medication,
        confidence=extracted.confidence,
    )
    db.session.add(report)
    db.session.flush()

    # ── Map abnormal values onto the body ─────────────────────────
    if extracted.abnormal:
        organ = _organ_for(extracted.abnormal)
        if organ:
            db.session.add(
                Finding(
                    user_id=user.id,
                    organ=organ,
                    conclusion=extracted.abnormal_summary,
                    annotation=f"{len(extracted.abnormal)} abnormal values",
                    severity="high" if extracted.critical else "medium",
                    source="report",
                    source_id=report.id,
                )
            )

    db.session.commit()

    payload = report.to_dict()

    # An ambiguous handwritten prescription is the single most dangerous thing
    # this system can encounter. Metformin and Metoprolol look identical in a
    # hurried scrawl and do very different things. Say so, loudly.
    if extracted.has_ambiguous_medication:
        payload["warning"] = (
            "Some handwriting on this prescription is ambiguous. Omni will not "
            "guess between drugs — please confirm with your pharmacist."
        )

    return ok(payload, status=201)


@report_bp.get("")
@require_auth
def list_reports():
    user = current_user()
    items = (
        Report.query.filter_by(user_id=user.id)
        .order_by(Report.uploaded_at.desc())
        .all()
    )
    return ok([r.to_dict() for r in items])


@report_bp.get("/<rid>")
@require_auth
def get_report(rid):
    user = current_user()
    r = Report.query.filter_by(id=rid, user_id=user.id).first()
    if not r:
        return error("No such report.", 404)
    return ok(r.to_dict())


def _organ_for(abnormal):
    """Cheap keyword map. The LLM organ_mapper is better; this is the fast path."""
    names = " ".join(b.get("name", "").lower() for b in abnormal)

    table = {
        "liver": ("alt", "ast", "bilirubin", "alp", "ggt", "albumin"),
        "kidneys": ("creatinine", "urea", "egfr", "bun"),
        "heart": ("troponin", "cholesterol", "ldl", "hdl", "triglyceride"),
        "blood": ("haemoglobin", "hemoglobin", "wbc", "platelet", "rbc", "hba1c"),
        "thyroid": ("tsh", "t3", "t4"),
        "pancreas": ("amylase", "lipase", "glucose"),
    }

    for organ, keys in table.items():
        if any(k in names for k in keys):
            return organ
    return None
