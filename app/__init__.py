
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

        # crear tablas
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

                ("A-1", 37.3826, -5.96005),
                ("A-2", 37.4076, -5.98659),
                ("A-3", 37.361, -5.97997),
                ("A-4", 37.3189, -5.96986),
                ("A-5", 37.4128, -5.92805),

                ("P-1", 37.3757, -6.00524),
                ("P-2", 37.3994, -5.92524),
                ("P-3", 37.3815, -5.96494),
                ("P-4", 37.3249, -5.96473),
                ("P-5", 37.4168, -6.00736),

                ("B-1", 37.385, -5.98468),
                ("B-2", 37.423, -5.9665),
                ("B-3", 37.361, -5.95946),
                ("B-4", 37.3675, -6.00582),
                ("B-5", 37.3549, -5.98848)
            ]

            for name, lat, lon in resources:

                db.session.add(
                    Resource(
                        name=name,
                        latitude=lat,
                        longitude=lon
                    )
                )

            db.session.commit()

            print("Base de datos inicializada")

    return app