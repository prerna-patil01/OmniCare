"""
Video consultation rooms.

Uses a Jitsi Meet room link — no API key, no account, works instantly. A unique
room name per appointment, opened in-app or in the browser. Voice-call assistance
(an AI answering a phone) is a multi-week telephony build (Twilio Voice + a
real-time model); it is stubbed here with an honest status rather than faked.
"""

import hashlib


def video_room(appointment_id: str, doctor_name: str = "") -> dict:
    """A deterministic, unguessable Jitsi room for this appointment."""
    slug = hashlib.sha256(f"omnicare:{appointment_id}".encode()).hexdigest()[:16]
    room = f"OmniCare-{slug}"
    return {
        "provider": "jitsi",
        "room": room,
        "url": f"https://meet.jit.si/{room}",
        "join_in_app": f"jitsi-meet://{room}",
        "note": "No account needed — the link opens the room directly.",
    }


def voice_assist(appointment_id: str) -> dict:
    """
    Voice-call assistance. Stubbed, honestly.

    A live AI phone assistant needs Twilio Voice, a streaming STT/TTS pipeline,
    and a real-time model — weeks of work. The architecture point stands; the
    live line does not exist yet.
    """
    return {
        "provider": "twilio_voice",
        "status": "architected_not_live",
        "note": (
            "Voice-call assistance requires a telephony pipeline (Twilio Voice + "
            "streaming speech). Video consultation is live; voice is the next build."
        ),
    }
