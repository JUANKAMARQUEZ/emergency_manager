from app import create_app
from app.extensions import db

from app.models import (
    Role,
    User,
    IncidentType,
    Resource
)

from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():

    # Crear tablas
    db.create_all()

    # -------------------------
    # ROLES
    # -------------------------

    admin_role = Role(name="administrador")
    user_role = Role(name="usuario")

    db.session.add(admin_role)
    db.session.add(user_role)

    # -------------------------
    # ADMIN
    # -------------------------

    admin = User(

        name="Juan Carlos Márquez",

        email="admin@gmail.com",

        password=generate_password_hash("admin123"),

        role=admin_role
    )

    db.session.add(admin)

    # -------------------------
    # TIPOS INCIDENCIA
    # -------------------------

    types = [

        "Incendio",

        "Asistencia Sanitaria",

        "Incidencia de Tráfico",

        "Seguridad Ciudadana",

        "Otros"
    ]

    for t in types:

        db.session.add(
            IncidentType(name=t)
        )

    # -------------------------
    # RECURSOS
    # -------------------------

    resources = [

        "A-1",

        "A-2",

        "A-3",

        "P-1",

        "P-2",

        "P-3",

        "B-1",

        "B-2",

        "B-3"
    ]

    for r in resources:

        db.session.add(
            Resource(name=r)
        )

    db.session.commit()

    print("Base de datos inicializada correctamente")