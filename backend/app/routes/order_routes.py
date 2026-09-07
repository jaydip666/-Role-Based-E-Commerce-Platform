from flask import Blueprint

from app.controllers import order_controller
from app.middleware.auth_middleware import authenticate_user

order_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@order_bp.route("", methods=["GET"])
@authenticate_user
def list_orders():
    return order_controller.list_orders()


@order_bp.route("/<order_id>", methods=["GET"])
@authenticate_user
def get_order(order_id):
    return order_controller.get_order(order_id)
