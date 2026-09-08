from flask import Blueprint, request

from app.controllers import auth_controller
from app.middleware.auth_middleware import authenticate_user

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    return auth_controller.register(request.get_json(silent=True))


@auth_bp.route("/login", methods=["POST"])
def login():
    return auth_controller.login(request.get_json(silent=True))


@auth_bp.route("/me", methods=["GET"])
@authenticate_user
def me():
    return auth_controller.me()


@auth_bp.route("/me", methods=["PUT"])
@authenticate_user
def update_me():
    return auth_controller.update_profile(request.get_json(silent=True))
