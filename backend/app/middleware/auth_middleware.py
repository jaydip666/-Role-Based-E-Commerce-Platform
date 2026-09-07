"""Authentication and role-based authorization middleware.

This is the single source of truth for backend security: every protected
route MUST go through `authenticate_user`, and role checks MUST use one
of the `require_*` decorators. The frontend hides buttons/pages for UX
only — it is never trusted, and a direct API call from a malicious
client is still blocked here.
"""
from functools import wraps

import jwt
from flask import g, request

from app.models.roles import ADMIN, SALES_PERSON
from app.models.user import find_user_by_id
from app.utils.object_id import to_object_id
from app.utils.responses import error
from app.utils.security import decode_token


def _extract_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ", 1)[1].strip()


def authenticate_user(f):
    """Validates the JWT and attaches the current user to flask.g.current_user.

    Handles: missing token (401), invalid token (401), expired token (401),
    and a token referring to a user that no longer exists (401).
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            return error("Authentication token is missing", 401)

        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return error("Authentication token has expired", 401)
        except jwt.InvalidTokenError:
            return error("Authentication token is invalid", 401)

        user_object_id = to_object_id(payload.get("sub"))
        if not user_object_id:
            return error("Authentication token is invalid", 401)

        user = find_user_by_id(user_object_id)
        if not user:
            return error("User for this token no longer exists", 401)

        g.current_user = user
        g.current_user_id = user["_id"]
        g.current_user_role = user["role"]
        return f(*args, **kwargs)

    return decorated


def require_role(*allowed_roles):
    """Must be used AFTER authenticate_user in the decorator chain."""

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            role = getattr(g, "current_user_role", None)
            if role is None:
                return error("Authentication required", 401)
            if role not in allowed_roles:
                return error("You do not have permission to perform this action", 403)
            return f(*args, **kwargs)

        return decorated

    return decorator


def require_admin(f):
    return require_role(ADMIN)(f)


def require_sales_person(f):
    return require_role(SALES_PERSON)(f)


def require_admin_or_sales(f):
    return require_role(ADMIN, SALES_PERSON)(f)
