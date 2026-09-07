from flask import g

from app.models.order import orders_collection, serialize_order
from app.models.roles import ADMIN, SALES_PERSON
from app.utils.object_id import to_object_id
from app.utils.responses import error, success


def list_orders():
    role = g.current_user_role
    if role == ADMIN:
        query = {}
    elif role == SALES_PERSON:
        query = {"items.seller_id": g.current_user_id}
    else:
        query = {"user_id": g.current_user_id}

    cursor = orders_collection().find(query).sort("created_at", -1)
    orders = [serialize_order(o) for o in cursor]
    return success({"orders": orders, "count": len(orders)})


def get_order(order_id):
    object_id = to_object_id(order_id)
    if not object_id:
        return error("Invalid order id", 400)

    order = orders_collection().find_one({"_id": object_id})
    if not order:
        return error("Order not found", 404)

    role = g.current_user_role
    if role == ADMIN:
        pass
    elif role == SALES_PERSON:
        seller_ids = {item.get("seller_id") for item in order.get("items", [])}
        if g.current_user_id not in seller_ids:
            return error("You do not have permission to view this order", 403)
    else:
        if order.get("user_id") != g.current_user_id:
            return error("You do not have permission to view this order", 403)

    return success({"order": serialize_order(order)})
