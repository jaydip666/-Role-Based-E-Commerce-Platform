from datetime import datetime, timezone

from app.extensions import get_db


def carts_collection():
    return get_db().carts


def ensure_indexes():
    carts_collection().create_index("user_id", unique=True)


def get_or_create_cart(user_id):
    cart = carts_collection().find_one({"user_id": user_id})
    if cart:
        return cart
    now = datetime.now(timezone.utc)
    cart = {"user_id": user_id, "items": [], "created_at": now, "updated_at": now}
    result = carts_collection().insert_one(cart)
    cart["_id"] = result.inserted_id
    return cart


def serialize_cart(cart, product_lookup):
    """product_lookup: dict[str product_id] -> serialized product (or None if deleted)."""
    items = []
    subtotal = 0.0
    for item in cart.get("items", []):
        product = product_lookup.get(str(item["product_id"]))
        if not product:
            continue
        line_total = product["price"] * item["quantity"]
        subtotal += line_total
        items.append({
            "product_id": str(item["product_id"]),
            "name": product["name"],
            "image_url": product["image_url"],
            "price": product["price"],
            "stock": product["stock"],
            "quantity": item["quantity"],
            "subtotal": round(line_total, 2),
        })
    return {
        "items": items,
        "item_count": sum(i["quantity"] for i in items),
        "subtotal": round(subtotal, 2),
        "total": round(subtotal, 2),
    }
