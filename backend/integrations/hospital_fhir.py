"""
Hospital FHIR interoperability.

Real hospital record exchange speaks FHIR R4. Building a live FHIR client needs a
hospital partner and a sandbox neither of which exists for a hackathon. This
stub shows the shape — a discharge summary as a FHIR-ish bundle — so the
architecture reads as interoperable, honestly labelled.
"""


def discharge_summary_bundle(user, triage_record) -> dict:
    """Assemble a minimal FHIR-shaped bundle for a receiving clinician."""
    return {
        "resourceType": "Bundle",
        "type": "document",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "name": [{"text": user.name}],
                    "gender": (user.profile.gender or "").lower() if user.profile else None,
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "code": {"text": triage_record.clinical_term},
                    "note": [{"text": triage_record.conclusion}],
                }
            },
        ],
        "note": "FHIR-shaped demo bundle. Live exchange requires a hospital FHIR endpoint.",
    }
