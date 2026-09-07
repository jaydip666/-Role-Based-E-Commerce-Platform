from flask import Blueprint, request

from app.controllers import wishlist_controller
from app.middleware.auth_middleware import authenticate_user

wishlist_bp = Blueprint("wishlist", __name__, url_prefix="/api/wishlist")


@wishlist_bp.route("", methods=["GET"])
@authenticate_user
def get_wishlist():
    return wishlist_controller.get_wishlist()


@wishlist_bp.route("", methods=["POST"])
@authenticate_user
def add_to_wishlist():
    return wishlist_controller.add_to_wishlist(request.get_json(silent=True))


@wishlist_bp.route("/<product_id>", methods=["DELETE"])
@authenticate_user
def remove_from_wishlist(product_id):
    return wishlist_controller.remove_from_wishlist(product_id)
