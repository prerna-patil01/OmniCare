"""
JWT authentication.
"""

from datetime import datetime
from functools import wraps

import jwt
from flask import current_app, g, request

from models import User
from utils.responses import error


def generate_token(user_id: str) -> str:
    cfg = current_app.config
    return jwt.encode(
        {
            "sub": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + cfg["JWT_EXPIRY"],
        },
        cfg["JWT_SECRET"],
        algorithm=cfg["JWT_ALGORITHM"],
    )


def verify_token(token: str) -> str | None:
    cfg = current_app.config
    try:
        payload = jwt.decode(
            token, cfg["JWT_SECRET"], algorithms=[cfg["JWT_ALGORITHM"]]
        )
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


def current_user() -> User | None:
    """
    Resolve the caller.

    Resolve only a verified bearer token.
    """
    if hasattr(g, "user"):
        return g.user

    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        user_id = verify_token(header[7:])
        if user_id:
            g.user = User.query.get(user_id)
            return g.user

    return None


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return error("Authentication required.", 401)
        return fn(*args, **kwargs)

    return wrapper
