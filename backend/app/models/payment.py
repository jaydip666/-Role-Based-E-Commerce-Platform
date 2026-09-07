"""Temporary holding record between 'create Razorpay order' and 'verify
payment'. Keeps a trusted, server-computed snapshot of what the user was
charged for so the real order can be built from it only after the payment
signature has been verified.
"""
from datetime import datetime, timezone

from app.extensions import get_db


def pending_payments_collection():
    return get_db().pending_payments


def create_pending_payment(user_id, razorpay_order_id, items, total_amount):
    now = datetime.now(timezone.utc)
    doc = {
        "user_id": user_id,
        "razorpay_order_id": razorpay_order_id,
        "items": items,
        "total_amount": total_amount,
        "consumed": False,
        "created_at": now,
    }
    result = pending_payments_collection().insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def find_pending_payment(user_id, razorpay_order_id):
    return pending_payments_collection().find_one({
        "user_id": user_id,
        "razorpay_order_id": razorpay_order_id,
        "consumed": False,
    })


def mark_consumed(pending_id):
    pending_payments_collection().update_one({"_id": pending_id}, {"$set": {"consumed": True}})
