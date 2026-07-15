"""
ABHA / ABDM.

Sandbox access requires organisation registration with the National Health
Authority and takes weeks. The ABHA number is stored and masked; the live ABDM
verification handshake is stubbed. In the pitch this is the point to say the
architecture is ABDM-ready — which is what matters — rather than claiming a live
token nobody could have obtained in a weekend.
"""


def verify(abha_id: str) -> dict:
    """Stub. Real ABDM verification hits the gateway with an org token."""
    if not abha_id:
        return {"verified": False, "reason": "No ABHA supplied."}

    # Format check only — a real check calls the ABDM gateway.
    digits = abha_id.replace("-", "")
    looks_valid = digits.isdigit() and len(digits) == 14

    return {
        "verified": looks_valid,
        "abha_id": f"····{abha_id[-4:]}",
        "note": "Format-checked only. Live ABDM verification requires NHA org onboarding.",
    }
