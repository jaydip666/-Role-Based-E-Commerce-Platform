"""Razorpay checkout flow.

1. create_order  — server reads the user's cart, recomputes the amount from
   trusted product prices in MongoDB (the frontend's numbers are NEVER
   trusted), creates a Razorpay order, and stores a snapshot of what is
   being purchased in `pending_payments`.
2. verify_payment — recomputes the Razorpay signature server-side. Only if
   it matches does a real `orders` document get created, the cart cleared,
   and the payment marked successful. An invalid signature never creates a
   successful order.
"""
from flask import g

from app.config import config
from app.models.cart import carts_collection, get_or_create_cart
from app.models.order import new_order_document, orders_collection, serialize_order
from app.models.payment import create_pending_payment, find_pending_payment, mark_consumed
from app.models.product import products_collection
from app.services.razorpay_service import PaymentError, create_razorpay_order, verify_payment_signature
from app.utils.responses import error, success


def checkout_create_order():
    cart = get_or_create_cart(g.current_user_id)
    if not cart.get("items"):
        return error("Your cart is empty", 400)

    product_ids = [item["product_id"] for item in cart["items"]]
    products = {p["_id"]: p for p in products_collection().find({"_id": {"$in": product_ids}})}

    order_items = []
    total_amount = 0.0
    for cart_item in cart["items"]:
        product = products.get(cart_item["product_id"])
        if not product:
            return error("One or more products in your cart no longer exist", 409)
        if product.get("stock", 0) < cart_item["quantity"]:
            return error(f"'{product['name']}' has insufficient stock", 409)

        subtotal = round(product["price"] * cart_item["quantity"], 2)
        total_amount += subtotal
        order_items.append({
            "product_id": product["_id"],
            "seller_id": product.get("owner_id"),
            "product_name": product["name"],
            "quantity": cart_item["quantity"],
            "price": product["price"],
            "subtotal": subtotal,
        })

    total_amount = round(total_amount, 2)
    if total_amount <= 0:
        return error("Order amount must be greater than zero", 400)

    try:
        razorpay_order = create_razorpay_order(total_amount, receipt=f"user_{g.current_user_id}")
    except PaymentError as exc:
        return error(str(exc), 502)

    create_pending_payment(g.current_user_id, razorpay_order["id"], order_items, total_amount)

    return success({
        "razorpay_order_id": razorpay_order["id"],
        "amount": razorpay_order["amount"],
        "currency": razorpay_order["currency"],
        "key_id": config.RAZORPAY_KEY_ID,
    }, "Razorpay order created", 201)


def verify_payment(data):
    data = data or {}
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_signature = data.get("razorpay_signature")

    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return error("razorpay_order_id, razorpay_payment_id and razorpay_signature are required", 400)

    is_valid = verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)
    if not is_valid:
        return error("Payment signature verification failed. Payment not confirmed.", 400)

    pending = find_pending_payment(g.current_user_id, razorpay_order_id)
    if not pending:
        return error("No matching pending payment found for this order", 404)

    order_document = new_order_document(
        user_id=g.current_user_id,
        customer_name=g.current_user.get("name"),
        items=pending["items"],
        total_amount=pending["total_amount"],
        razorpay_order_id=razorpay_order_id,
    )
    order_document["razorpay_payment_id"] = razorpay_payment_id
    order_document["payment_status"] = "paid"
    order_document["order_status"] = "Confirmed"

    result = orders_collection().insert_one(order_document)
    order_document["_id"] = result.inserted_id

    for item in pending["items"]:
        products_collection().update_one(
            {"_id": item["product_id"]}, {"$inc": {"stock": -item["quantity"]}}
        )

    mark_consumed(pending["_id"])
    cart = get_or_create_cart(g.current_user_id)
    carts_collection().update_one({"_id": cart["_id"]}, {"$set": {"items": []}})

    return success({"order": serialize_order(order_document)}, "Payment verified and order created", 201)
