"""Uniform response envelopes. The frontend should never have to guess."""

from flask import jsonify


def ok(data=None, **extra):
    payload = {"ok": True}
    if data is not None:
        payload["data"] = data
    payload.update(extra)
    return jsonify(payload), 200


def error(message, status=400, **extra):
    return jsonify({"ok": False, "error": message, **extra}), status
