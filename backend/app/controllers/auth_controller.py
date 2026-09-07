from flask import g

from app.models.roles import USER
from app.models.user import create_user, find_user_by_email, serialize_user
from app.utils.responses import error, success
from app.utils.security import generate_token, hash_password, verify_password
from app.validators.validators import validate_email, validate_name, validate_password


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
