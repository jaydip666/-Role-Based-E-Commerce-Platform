from flask import g

from app.models.order import orders_collection, serialize_order
from app.models.product import products_collection, serialize_product
from app.utils.responses import success


def list_own_products():
    cursor = products_collection().find({"owner_id": g.current_user_id}).sort("created_at", -1)
    products = [serialize_product(p) for p in cursor]
    return success({"products": products, "count": len(products)})


def list_relevant_orders():
    cursor = orders_collection().find({"items.seller_id": g.current_user_id}).sort("created_at", -1)
    orders = []
    for order in cursor:
        serialized = serialize_order(order)
        # Only surface this seller's own line items, not the whole order.
        serialized["items"] = [
            item for item in serialized["items"] if item["seller_id"] == str(g.current_user_id)
        ]
        orders.append(serialized)
    return success({"orders": orders, "count": len(orders)})


def get_stats():
    own_products = list(products_collection().find({"owner_id": g.current_user_id}))

    orders = list(orders_collection().find({"items.seller_id": g.current_user_id, "payment_status": "paid"}))
    total_sales = 0.0
    total_units_sold = 0
    for order in orders:
        for item in order.get("items", []):
            # Only this seller's own line items count — an order can mix
            # products from multiple sellers, and each seller must only see
            # their own share, never the full order total.
            if item.get("seller_id") == g.current_user_id:
                total_sales += item.get("subtotal", 0)
                total_units_sold += item.get("quantity", 0)

    recent_orders = [serialize_order(o) for o in orders[:5]]

    return success({
        "total_products": len(own_products),
        "total_orders": len(orders),
        "total_units_sold": total_units_sold,
        "total_sales": round(total_sales, 2),
        "recent_orders": recent_orders,
    })
