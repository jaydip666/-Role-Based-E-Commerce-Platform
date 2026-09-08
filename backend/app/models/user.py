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
        "phone": "",
        "address": "",
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


# Fields a user is allowed to change about themselves via the profile endpoint.
# Deliberately excludes role, password_hash, email and any other admin-controlled field.
PROFILE_FIELDS = ("name", "phone", "address")


def update_user_profile(user_id, updates):
    """Updates only PROFILE_FIELDS for the given user_id. Caller must have
    already derived user_id from the authenticated JWT, never from client input."""
    fields = {k: v for k, v in updates.items() if k in PROFILE_FIELDS}
    if not fields:
        return find_user_by_id(user_id)
    fields["updated_at"] = datetime.now(timezone.utc)
    users_collection().update_one({"_id": user_id}, {"$set": fields})
    return find_user_by_id(user_id)


def serialize_user(user):
    """Never expose password_hash in API responses."""
    if not user:
        return None
    return {
        "id": str(user["_id"]),
        "name": user.get("name"),
        "email": user.get("email"),
        "role": user.get("role"),
        "phone": user.get("phone", ""),
        "address": user.get("address", ""),
        "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
    }
