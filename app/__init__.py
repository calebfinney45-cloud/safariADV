"""
create_app() is the function that builds the actual Flask app:
  1. Reads config from config.py
  2. Initializes all extensions
  3. Registers all application models
  4. Registers all API blueprints
"""

from flask import Flask, jsonify

from app.config import Config
from app.extensions import db, migrate, jwt, mail, bcrypt, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ---------------------------------------------------------
    # Extensions
    # ---------------------------------------------------------

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)

    cors.init_app(
        app,
        origins=app.config["CORS_ORIGINS"],
        supports_credentials=True,
    )

    # ---------------------------------------------------------
    # Models
    # ---------------------------------------------------------

    from app import models  # noqa: F401

    # ---------------------------------------------------------
    # Blueprints
    # ---------------------------------------------------------

    from app.routes.auth import auth_bp
    from app.routes.trip_packages import trip_packages_bp
    from app.routes.bookings import bookings_bp
    from app.routes.admin import admin_bp
    from app.routes.reviews import reviews_bp
    from app.routes.favorites import favorites_bp
    from app.routes.agents import agents_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(trip_packages_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(favorites_bp)
    app.register_blueprint(agents_bp)

    # ---------------------------------------------------------
    # JWT error handlers
    # ---------------------------------------------------------

    @jwt.unauthorized_loader
    def _missing_token(reason):
        return jsonify({
            "error": "Authentication required."
        }), 401

    @jwt.invalid_token_loader
    def _invalid_token(reason):
        return jsonify({
            "error": "Invalid authentication token."
        }), 401

    @jwt.expired_token_loader
    def _expired_token(jwt_header, jwt_payload):
        return jsonify({
            "error": "Your session has expired. Please log in again."
        }), 401

    # ---------------------------------------------------------
    # Generic error handlers
    # ---------------------------------------------------------

    @app.errorhandler(404)
    def _not_found(e):
        return jsonify({
            "error": "Not found."
        }), 404

    @app.errorhandler(405)
    def _method_not_allowed(e):
        return jsonify({
            "error": "Method not allowed."
        }), 405

    @app.errorhandler(500)
    def _server_error(e):
        return jsonify({
            "error": "Something went wrong on our end."
        }), 500

    # ---------------------------------------------------------
    # Health check
    # ---------------------------------------------------------

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok"
        }), 200

    return app