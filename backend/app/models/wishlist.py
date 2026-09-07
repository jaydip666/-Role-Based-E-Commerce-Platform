from datetime import datetime, timezone

from app.extensions import get_db


def wishlists_collection():
    return get_db().wishlists


def ensure_indexes():
    wishlists_collection().create_index("user_id", unique=True)


def get_or_create_wishlist(user_id):
    wishlist = wishlists_collection().find_one({"user_id": user_id})
    if wishlist:
        return wishlist
    now = datetime.now(timezone.utc)
    wishlist = {"user_id": user_id, "products": [], "created_at": now, "updated_at": now}
    result = wishlists_collection().insert_one(wishlist)
    wishlist["_id"] = result.inserted_id
    return wishlist
