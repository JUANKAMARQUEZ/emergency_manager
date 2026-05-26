
from flask import Flask
from config import Config
from .extensions import db, login_manager


def create_app():

    app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
    )

    app.config.from_object(Config)

    db.init_app(app)

    login_manager.init_app(app)

    from . import models

    # Registrar rutas
    from .routes.auth_routes import auth_bp
    from .routes.incident_routes import incident_bp
    from .routes.user_routes import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(incident_bp)
    app.register_blueprint(user_bp)

    return app