from datetime import datetime, timezone

from flask import g

from app.models.cart import carts_collection, get_or_create_cart, serialize_cart
from app.models.product import products_collection, serialize_product
from app.utils.object_id import to_object_id
from app.utils.responses import error, success
from app.validators.validators import validate_quantity


def _build_product_lookup(cart):
    product_ids = [item["product_id"] for item in cart.get("items", [])]
    products = products_collection().find({"_id": {"$in": product_ids}})
    return {str(p["_id"]): serialize_product(p) for p in products}


def get_cart():
    cart = get_or_create_cart(g.current_user_id)
    lookup = _build_product_lookup(cart)
    return success(serialize_cart(cart, lookup))


def add_item(data):
    product_id = to_object_id((data or {}).get("product_id"))
    quantity = (data or {}).get("quantity", 1)

    if not product_id:
        return error("A valid product_id is required", 400)
    if not validate_quantity(quantity):
        return error("quantity must be a positive integer", 400)
    quantity = int(quantity)

    product = products_collection().find_one({"_id": product_id})
    if not product:
        return error("Product not found", 404)

    cart = get_or_create_cart(g.current_user_id)
    existing = next((i for i in cart["items"] if i["product_id"] == product_id), None)
    new_quantity = quantity + (existing["quantity"] if existing else 0)

    if product.get("stock", 0) < new_quantity:
        return error(f"Only {product.get('stock', 0)} unit(s) left in stock", 409)

    if existing:
        carts_collection().update_one(
            {"_id": cart["_id"], "items.product_id": product_id},
            {"$set": {"items.$.quantity": new_quantity, "updated_at": datetime.now(timezone.utc)}},
        )
    else:
        carts_collection().update_one(
            {"_id": cart["_id"]},
            {
                "$push": {"items": {"product_id": product_id, "quantity": quantity}},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
        )

    updated_cart = carts_collection().find_one({"_id": cart["_id"]})
    lookup = _build_product_lookup(updated_cart)
    return success(serialize_cart(updated_cart, lookup), "Product added to cart", 201)


def update_item(product_id, data):
    object_id = to_object_id(product_id)
    quantity = (data or {}).get("quantity")

    if not object_id:
        return error("Invalid product id", 400)
    if not validate_quantity(quantity):
        return error("quantity must be a positive integer", 400)
    quantity = int(quantity)

    product = products_collection().find_one({"_id": object_id})
    if not product:
        return error("Product not found", 404)
    if product.get("stock", 0) < quantity:
        return error(f"Only {product.get('stock', 0)} unit(s) left in stock", 409)

    cart = get_or_create_cart(g.current_user_id)
    result = carts_collection().update_one(
        {"_id": cart["_id"], "items.product_id": object_id},
        {"$set": {"items.$.quantity": quantity, "updated_at": datetime.now(timezone.utc)}},
    )
    if result.matched_count == 0:
        return error("Product is not in your cart", 404)

    updated_cart = carts_collection().find_one({"_id": cart["_id"]})
    lookup = _build_product_lookup(updated_cart)
    return success(serialize_cart(updated_cart, lookup), "Cart updated")


def remove_item(product_id):
    object_id = to_object_id(product_id)
    if not object_id:
        return error("Invalid product id", 400)

    cart = get_or_create_cart(g.current_user_id)
    carts_collection().update_one(
        {"_id": cart["_id"]},
        {"$pull": {"items": {"product_id": object_id}}, "$set": {"updated_at": datetime.now(timezone.utc)}},
    )
    updated_cart = carts_collection().find_one({"_id": cart["_id"]})
    lookup = _build_product_lookup(updated_cart)
    return success(serialize_cart(updated_cart, lookup), "Item removed from cart")
