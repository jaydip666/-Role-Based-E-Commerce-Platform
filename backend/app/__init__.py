from flask import Flask
from flask_cors import CORS

from app import extensions
from app.config import config
from app.utils.responses import error


def create_app(db=None):
    """Application factory.

    `db` lets callers (namely the test suite) inject an already-constructed
    database — e.g. an isolated mongomock instance — instead of connecting
    to the real MongoDB server configured via MONGODB_URI. Production and
    local development never pass this and get a real connection.
    """
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    CORS(
        app,
        resources={r"/api/*": {"origins": config.CORS_ORIGINS}},
        supports_credentials=True,
    )

    if db is not None:
        extensions.set_db(db)
    else:
        extensions.init_mongo()
    extensions.init_cloudinary()
    _ensure_indexes()

    _register_blueprints(app)
    _register_error_handlers(app)

    @app.route("/api/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    return app


def _ensure_indexes():
    from app.models import cart, order, product, user, wishlist

    user.ensure_indexes()
    product.ensure_indexes()
    cart.ensure_indexes()
    wishlist.ensure_indexes()
    order.ensure_indexes()


def _register_blueprints(app):
    from app.routes.admin_routes import admin_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.cart_routes import cart_bp
    from app.routes.order_routes import order_bp
    from app.routes.payment_routes import payment_bp
    from app.routes.product_routes import product_bp
    from app.routes.sales_routes import sales_bp
    from app.routes.wishlist_routes import wishlist_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(payment_bp)


def _register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return error("Bad request", 400)

    @app.errorhandler(401)
    def unauthorized(e):
        return error("Unauthorized", 401)

    @app.errorhandler(403)
    def forbidden(e):
        return error("Forbidden", 403)

    @app.errorhandler(404)
    def not_found(e):
        return error("Resource not found", 404)

    @app.errorhandler(409)
    def conflict(e):
        return error("Conflict", 409)

    @app.errorhandler(500)
    def server_error(e):
        # Never leak stack traces to the client.
        app.logger.exception("Unhandled server error")
        return error("Internal server error", 500)
