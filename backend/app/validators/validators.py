import re

from email_validator import EmailNotValidError, validate_email as _validate_email

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email):
    if not email or not isinstance(email, str):
        return False
    try:
        _validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return bool(EMAIL_RE.match(email))


def validate_password(password):
    """At least 6 characters, at least one letter and one number."""
    if not password or not isinstance(password, str):
        return False
    if len(password) < 6:
        return False
    return bool(re.search(r"[A-Za-z]", password)) and bool(re.search(r"\d", password))


def validate_name(name):
    return bool(name) and isinstance(name, str) and 2 <= len(name.strip()) <= 100


def validate_price(price):
    try:
        value = float(price)
        return value >= 0
    except (TypeError, ValueError):
        return False


def validate_stock(stock):
    try:
        value = int(stock)
        return value >= 0
    except (TypeError, ValueError):
        return False


def validate_quantity(quantity):
    try:
        value = int(quantity)
        return value >= 1
    except (TypeError, ValueError):
        return False


def validate_product_payload(data, partial=False):
    """Returns a list of field errors, empty list means valid."""
    errors = []
    if not partial or "name" in data:
        if not data.get("name") or not isinstance(data.get("name"), str) or len(data["name"].strip()) < 2:
            errors.append("name must be a string with at least 2 characters")
    if not partial or "description" in data:
        if not data.get("description") or not isinstance(data.get("description"), str):
            errors.append("description is required")
    if not partial or "price" in data:
        if not validate_price(data.get("price")):
            errors.append("price must be a non-negative number")
    if not partial or "category" in data:
        if not data.get("category") or not isinstance(data.get("category"), str):
            errors.append("category is required")
    if not partial or "stock" in data:
        if not validate_stock(data.get("stock", 0)):
            errors.append("stock must be a non-negative integer")
    return errors
