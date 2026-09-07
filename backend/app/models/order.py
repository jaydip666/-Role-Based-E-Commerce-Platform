from datetime import datetime, timezone

from app.extensions import get_db

ORDER_STATUSES = ("Pending", "Confirmed", "Processing", "Shipped", "Delivered", "Cancelled")
PAYMENT_STATUSES = ("created", "paid", "failed")


def orders_collection():
    return get_db().orders


def ensure_indexes():
    orders_collection().create_index("user_id")
    orders_collection().create_index("items.seller_id")
    orders_collection().create_index("razorpay_order_id")


def serialize_order(order):
    if not order:
        return None
    return {
        "id": str(order["_id"]),
        "user_id": str(order.get("user_id")),
        "customer_name": order.get("customer_name"),
        "items": [
            {
                "product_id": str(item.get("product_id")),
                "seller_id": str(item.get("seller_id")) if item.get("seller_id") else None,
                "product_name": item.get("product_name"),
                "quantity": item.get("quantity"),
                "price": item.get("price"),
                "subtotal": item.get("subtotal"),
            }
            for item in order.get("items", [])
        ],
        "total_amount": order.get("total_amount"),
        "razorpay_order_id": order.get("razorpay_order_id"),
        "razorpay_payment_id": order.get("razorpay_payment_id"),
        "payment_status": order.get("payment_status"),
        "order_status": order.get("order_status"),
        "created_at": order.get("created_at").isoformat() if order.get("created_at") else None,
        "updated_at": order.get("updated_at").isoformat() if order.get("updated_at") else None,
    }


def new_order_document(user_id, customer_name, items, total_amount, razorpay_order_id):
    now = datetime.now(timezone.utc)
    return {
        "user_id": user_id,
        "customer_name": customer_name,
        "items": items,
        "total_amount": total_amount,
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": None,
        "payment_status": "created",
        "order_status": "Pending",
        "created_at": now,
        "updated_at": now,
    }
