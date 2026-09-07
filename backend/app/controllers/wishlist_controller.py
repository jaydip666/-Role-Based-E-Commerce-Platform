from datetime import datetime, timezone

from flask import g

from app.models.product import products_collection, serialize_product
from app.models.wishlist import get_or_create_wishlist, wishlists_collection
from app.utils.object_id import to_object_id
from app.utils.responses import error, success


def get_wishlist():
    wishlist = get_or_create_wishlist(g.current_user_id)
    product_ids = wishlist.get("products", [])
    products = list(products_collection().find({"_id": {"$in": product_ids}}))
    serialized = [serialize_product(p) for p in products]
    return success({"products": serialized, "count": len(serialized)})


def add_to_wishlist(data):
    product_id = to_object_id((data or {}).get("product_id"))
    if not product_id:
        return error("A valid product_id is required", 400)

    product = products_collection().find_one({"_id": product_id})
    if not product:
        return error("Product not found", 404)

    wishlist = get_or_create_wishlist(g.current_user_id)
    if product_id in wishlist.get("products", []):
        return success(message="Product already in wishlist")

    wishlists_collection().update_one(
        {"_id": wishlist["_id"]},
        {"$addToSet": {"products": product_id}, "$set": {"updated_at": datetime.now(timezone.utc)}},
    )
    return success(message="Product added to wishlist", status=201)


def remove_from_wishlist(product_id):
    object_id = to_object_id(product_id)
    if not object_id:
        return error("Invalid product id", 400)

    wishlist = get_or_create_wishlist(g.current_user_id)
    wishlists_collection().update_one(
        {"_id": wishlist["_id"]},
        {"$pull": {"products": object_id}, "$set": {"updated_at": datetime.now(timezone.utc)}},
    )
    return success(message="Product removed from wishlist")
