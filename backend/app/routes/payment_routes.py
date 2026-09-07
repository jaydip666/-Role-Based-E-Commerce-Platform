from flask import Blueprint, request

from app.controllers import payment_controller
from app.middleware.auth_middleware import authenticate_user

payment_bp = Blueprint("payment", __name__, url_prefix="/api/payment")


@payment_bp.route("/create-order", methods=["POST"])
@authenticate_user
def create_order():
    return payment_controller.checkout_create_order()


@payment_bp.route("/verify", methods=["POST"])
@authenticate_user
def verify():
    return payment_controller.verify_payment(request.get_json(silent=True))
