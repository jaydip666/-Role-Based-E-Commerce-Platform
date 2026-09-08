from flask import g

from app.models.roles import USER
from app.models.user import create_user, find_user_by_email, serialize_user, update_user_profile
from app.utils.responses import error, success
from app.utils.security import generate_token, hash_password, verify_password
from app.validators.validators import (
    validate_address,
    validate_email,
    validate_name,
    validate_password,
    validate_phone,
)


def register(data):
    name = (data or {}).get("name", "").strip() if isinstance(data, dict) else ""
    email = (data or {}).get("email", "").strip().lower() if isinstance(data, dict) else ""
    password = (data or {}).get("password", "") if isinstance(data, dict) else ""

    errors = []
    if not validate_name(name):
        errors.append("name must be between 2 and 100 characters")
    if not validate_email(email):
        errors.append("a valid email is required")
    if not validate_password(password):
        errors.append("password must be at least 6 characters and include a letter and a number")
    if errors:
        return error("Validation failed", 400, errors)

    if find_user_by_email(email):
        return error("An account with this email already exists", 409)

    user = create_user(name=name, email=email, password_hash=hash_password(password), role=USER)
    token = generate_token(user["_id"], user["role"])
    return success({"token": token, "user": serialize_user(user)}, "Registration successful", 201)


def login(data):
    email = (data or {}).get("email", "").strip().lower() if isinstance(data, dict) else ""
    password = (data or {}).get("password", "") if isinstance(data, dict) else ""

    if not email or not password:
        return error("Email and password are required", 400)

    user = find_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return error("Invalid email or password", 401)

    token = generate_token(user["_id"], user["role"])
    return success({"token": token, "user": serialize_user(user)}, "Login successful", 200)


def me():
    return success({"user": serialize_user(g.current_user)})


def update_profile(data):
    """Updates the authenticated user's own profile.

    The user id comes only from g.current_user_id (derived from the JWT by
    authenticate_user) — any user_id/role/password_hash in `data` is ignored,
    so a user can never edit another account or escalate their own role.
    """
    data = data if isinstance(data, dict) else {}

    updates = {}
    errors = []

    if "name" in data:
        name = (data.get("name") or "").strip()
        if not validate_name(name):
            errors.append("name must be between 2 and 100 characters")
        else:
            updates["name"] = name

    if "phone" in data:
        phone = (data.get("phone") or "").strip()
        if not validate_phone(phone):
            errors.append("phone must be a valid phone number up to 20 characters")
        else:
            updates["phone"] = phone

    if "address" in data:
        address = (data.get("address") or "").strip()
        if not validate_address(address):
            errors.append("address must be at most 255 characters")
        else:
            updates["address"] = address

    if errors:
        return error("Validation failed", 400, errors)
    if not updates:
        return error("No valid profile fields provided", 400)

    updated_user = update_user_profile(g.current_user_id, updates)
    return success({"user": serialize_user(updated_user)}, "Profile updated successfully")
