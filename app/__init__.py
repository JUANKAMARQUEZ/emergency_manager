
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

    with app.app_context():

        from .models import (
            Role,
            User,
            IncidentType,
            Resource
        )

        from werkzeug.security import generate_password_hash

        # Crear tablas
        db.create_all()

        # Inicializar solo si está vacío
        if not Role.query.first():

            # Roles
            admin_role = Role(name="administrador")
            user_role = Role(name="usuario")

            db.session.add(admin_role)
            db.session.add(user_role)

            # Admin
            admin = User(

                name="Juan Carlos Márquez",

                email="admin@gmail.com",

                password=generate_password_hash(
                    "admin123"
                ),

                role=admin_role
            )

            db.session.add(admin)

            # Tipos incidencia
            types = [

                "Incendio",

                "Asistencia Sanitaria",

                "Incidencia de Tráfico",

                "Siniestro Vial",

                "Seguridad Ciudadana",

                "Otros"
            ]

            for t in types:
                db.session.add(
                    IncidentType(name=t)
                )

            # Recursos
            resources = [

                "A-1", "A-2", "A-3", "A-4", "A-5",

                "P-1", "P-2", "P-3", "P-4", "P-5",

                "B-1", "B-2", "B-3", "B-4", "B-5"
            ]

            for r in resources:
                db.session.add(
                    Resource(name=r)
                )

            db.session.commit()

            print("Base de datos inicializada")

    return app