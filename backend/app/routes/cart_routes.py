from flask import Blueprint, request

from app.controllers import cart_controller
from app.middleware.auth_middleware import authenticate_user

cart_bp = Blueprint("cart", __name__, url_prefix="/api/cart")


@cart_bp.route("", methods=["GET"])
@authenticate_user
def get_cart():
    return cart_controller.get_cart()


@cart_bp.route("", methods=["POST"])
@authenticate_user
def add_item():
    return cart_controller.add_item(request.get_json(silent=True))


@cart_bp.route("/<product_id>", methods=["PUT"])
@authenticate_user
def update_item(product_id):
    return cart_controller.update_item(product_id, request.get_json(silent=True))


@cart_bp.route("/<product_id>", methods=["DELETE"])
@authenticate_user
def remove_item(product_id):
    return cart_controller.remove_item(product_id)
