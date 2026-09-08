from datetime import datetime, timezone

from flask import g

from app.models.order import ORDER_STATUSES, orders_collection, serialize_order
from app.models.product import products_collection
from app.models.roles import ALL_ROLES
from app.models.user import serialize_user, update_user_profile, users_collection
from app.utils.object_id import to_object_id
from app.utils.responses import error, success
from app.validators.validators import validate_address, validate_name, validate_phone


def list_users():
    users = [serialize_user(u) for u in users_collection().find().sort("created_at", -1)]
    return success({"users": users, "count": len(users)})


def update_user_role(user_id, data):
    object_id = to_object_id(user_id)
    new_role = (data or {}).get("role")

    if not object_id:
        return error("Invalid user id", 400)
    if new_role not in ALL_ROLES:
        return error(f"role must be one of {', '.join(ALL_ROLES)}", 400)

    user = users_collection().find_one({"_id": object_id})
    if not user:
        return error("User not found", 404)

    users_collection().update_one(
        {"_id": object_id}, {"$set": {"role": new_role, "updated_at": datetime.now(timezone.utc)}}
    )
    updated = users_collection().find_one({"_id": object_id})
    return success({"user": serialize_user(updated)}, "User role updated")


def update_user(user_id, data):
    """Admin edits another user's safe profile fields.

    Only name/phone/address may change here — role has its own dedicated
    endpoint, and password_hash/email are never touched by this path.
    """
    object_id = to_object_id(user_id)
    if not object_id:
        return error("Invalid user id", 400)

    existing = users_collection().find_one({"_id": object_id})
    if not existing:
        return error("User not found", 404)

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

    updated = update_user_profile(object_id, updates)
    return success({"user": serialize_user(updated)}, "User updated successfully")


def delete_user(user_id):
    object_id = to_object_id(user_id)
    if not object_id:
        return error("Invalid user id", 400)

    # An admin's own account is only removable by another admin, never by itself,
    # so a compromised/careless admin session can't lock everyone out.
    if object_id == g.current_user_id:
        return error("You cannot delete your own account", 400)

    existing = users_collection().find_one({"_id": object_id})
    if not existing:
        return error("User not found", 404)

    users_collection().delete_one({"_id": object_id})
    return success(None, "User deleted successfully")


def list_all_orders():
    orders = [serialize_order(o) for o in orders_collection().find().sort("created_at", -1)]
    return success({"orders": orders, "count": len(orders)})


def update_order_status(order_id, data):
    object_id = to_object_id(order_id)
    new_status = (data or {}).get("order_status")

    if not object_id:
        return error("Invalid order id", 400)
    if new_status not in ORDER_STATUSES:
        return error(f"order_status must be one of {', '.join(ORDER_STATUSES)}", 400)

    order = orders_collection().find_one({"_id": object_id})
    if not order:
        return error("Order not found", 404)

    orders_collection().update_one(
        {"_id": object_id}, {"$set": {"order_status": new_status, "updated_at": datetime.now(timezone.utc)}}
    )
    updated = orders_collection().find_one({"_id": object_id})
    return success({"order": serialize_order(updated)}, "Order status updated")


def get_stats():
    total_users = users_collection().count_documents({})
    total_products = products_collection().count_documents({})
    all_orders = list(orders_collection().find({"payment_status": "paid"}))
    total_orders = len(all_orders)
    total_sales = round(sum(o.get("total_amount", 0) for o in all_orders), 2)

    recent_orders = [
        serialize_order(o) for o in orders_collection().find().sort("created_at", -1).limit(5)
    ]

    return success({
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_sales": total_sales,
        "recent_orders": recent_orders,
    })
