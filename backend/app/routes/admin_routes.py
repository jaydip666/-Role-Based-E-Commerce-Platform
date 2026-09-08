from flask import Blueprint, request

from app.controllers import admin_controller
from app.middleware.auth_middleware import authenticate_user, require_admin

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/users", methods=["GET"])
@authenticate_user
@require_admin
def list_users():
    return admin_controller.list_users()


@admin_bp.route("/users/<user_id>/role", methods=["PUT"])
@authenticate_user
@require_admin
def update_user_role(user_id):
    return admin_controller.update_user_role(user_id, request.get_json(silent=True))


@admin_bp.route("/users/<user_id>", methods=["PUT"])
@authenticate_user
@require_admin
def update_user(user_id):
    return admin_controller.update_user(user_id, request.get_json(silent=True))


@admin_bp.route("/users/<user_id>", methods=["DELETE"])
@authenticate_user
@require_admin
def delete_user(user_id):
    return admin_controller.delete_user(user_id)


@admin_bp.route("/orders", methods=["GET"])
@authenticate_user
@require_admin
def list_all_orders():
    return admin_controller.list_all_orders()


@admin_bp.route("/orders/<order_id>/status", methods=["PUT"])
@authenticate_user
@require_admin
def update_order_status(order_id):
    return admin_controller.update_order_status(order_id, request.get_json(silent=True))


@admin_bp.route("/stats", methods=["GET"])
@authenticate_user
@require_admin
def get_stats():
    return admin_controller.get_stats()
