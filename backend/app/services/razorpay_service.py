import hashlib
import hmac
import logging

from app.config import config
from app.extensions import get_razorpay_client

logger = logging.getLogger(__name__)


class PaymentError(Exception):
    pass


def create_razorpay_order(amount_in_rupees, receipt):
    """Amount is converted to paise (smallest currency unit) as Razorpay requires.

    The caller MUST compute amount_in_rupees from trusted server-side product
    data, never from a value sent by the frontend.
    """
    client = get_razorpay_client()
    amount_in_paise = int(round(amount_in_rupees * 100))
    try:
        order = client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": receipt,
            "payment_capture": 1,
        })
    except Exception as exc:
        # Log the full detail server-side only — connection/SSL/auth internals
        # must never reach the client (they'd leak infrastructure details).
        logger.exception("Razorpay order creation failed")
        raise PaymentError(
            "Could not start the payment. Please try again in a moment."
        ) from exc
    return order


def verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """Recomputes the HMAC-SHA256 signature Razorpay expects and compares it
    against the one returned by the frontend after checkout. This is the
    ONLY way payment success is trusted — a frontend claim alone is never
    sufficient to mark an order as paid.
    """
    payload = f"{razorpay_order_id}|{razorpay_payment_id}"
    expected_signature = hmac.new(
        key=config.RAZORPAY_KEY_SECRET.encode("utf-8"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected_signature, razorpay_signature or "")
