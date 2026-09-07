from flask import Blueprint, request

from app.controllers import product_controller
from app.middleware.auth_middleware import authenticate_user, require_admin_or_sales

product_bp = Blueprint("products", __name__, url_prefix="/api/products")


def _request_form_and_files():
    """Supports both multipart/form-data (with an image file) and plain JSON
    (image_url only) request bodies for product create/update."""
    if request.files:
        return request.form, request.files
    data = request.get_json(silent=True) or {}
    return data, {}


@product_bp.route("", methods=["GET"])
def list_products():
    return product_controller.list_products(request.args)


@product_bp.route("/<product_id>", methods=["GET"])
def get_product(product_id):
    return product_controller.get_product(product_id)


@product_bp.route("", methods=["POST"])
@authenticate_user
@require_admin_or_sales
def create_product():
    form, files = _request_form_and_files()
    return product_controller.create_product(form, files)


@product_bp.route("/<product_id>", methods=["PUT"])
@authenticate_user
@require_admin_or_sales
def update_product(product_id):
    form, files = _request_form_and_files()
    return product_controller.update_product(product_id, form, files)


@product_bp.route("/<product_id>", methods=["DELETE"])
@authenticate_user
@require_admin_or_sales
def delete_product(product_id):
    return product_controller.delete_product(product_id)
