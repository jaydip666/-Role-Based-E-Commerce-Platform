from datetime import datetime, timezone

from app.extensions import get_db


def products_collection():
    return get_db().products


def ensure_indexes():
    try:
        products_collection().create_index([("name", "text"), ("description", "text")])
    except Exception:
        # Text indexes aren't supported by every Mongo-compatible backend
        # (e.g. mongomock in tests); search falls back to regex matching.
        pass
    products_collection().create_index("category")
    products_collection().create_index("owner_id")


def serialize_product(product):
    if not product:
        return None
    return {
        "id": str(product["_id"]),
        "name": product.get("name"),
        "description": product.get("description"),
        "price": product.get("price"),
        "category": product.get("category"),
        "image_url": product.get("image_url"),
        "owner_id": str(product.get("owner_id")) if product.get("owner_id") else None,
        "owner_name": product.get("owner_name"),
        "stock": product.get("stock", 0),
        "created_at": product.get("created_at").isoformat() if product.get("created_at") else None,
        "updated_at": product.get("updated_at").isoformat() if product.get("updated_at") else None,
    }


def new_product_document(name, description, price, category, image_url, owner_id, owner_name, stock):
    now = datetime.now(timezone.utc)
    return {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "image_url": image_url,
        "owner_id": owner_id,
        "owner_name": owner_name,
        "stock": stock,
        "created_at": now,
        "updated_at": now,
    }
