from flask import Blueprint

from app.controllers import sales_controller
from app.middleware.auth_middleware import authenticate_user, require_sales_person

sales_bp = Blueprint("sales", __name__, url_prefix="/api/sales")


@sales_bp.route("/products", methods=["GET"])
@authenticate_user
@require_sales_person
def list_own_products():
    return sales_controller.list_own_products()


@sales_bp.route("/orders", methods=["GET"])
@authenticate_user
@require_sales_person
def list_relevant_orders():
    return sales_controller.list_relevant_orders()


@sales_bp.route("/stats", methods=["GET"])
@authenticate_user
@require_sales_person
def get_stats():
    return sales_controller.get_stats()
