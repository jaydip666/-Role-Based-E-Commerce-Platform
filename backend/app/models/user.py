from datetime import datetime, timezone

from app.extensions import get_db
from app.models.roles import USER


def users_collection():
    return get_db().users


def ensure_indexes():
    users_collection().create_index("email", unique=True)


def create_user(name, email, password_hash, role=USER):
    now = datetime.now(timezone.utc)
    user = {
        "name": name,
        "email": email.lower().strip(),
        "password_hash": password_hash,
        "role": role,
        "created_at": now,
        "updated_at": now,
    }
    result = users_collection().insert_one(user)
    user["_id"] = result.inserted_id
    return user


def find_user_by_email(email):
    return users_collection().find_one({"email": email.lower().strip()})


def find_user_by_id(user_id):
    return users_collection().find_one({"_id": user_id})


def serialize_user(user):
    """Never expose password_hash in API responses."""
    if not user:
        return None
    return {
        "id": str(user["_id"]),
        "name": user.get("name"),
        "email": user.get("email"),
        "role": user.get("role"),
        "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
    }
