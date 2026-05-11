from .extensions import db, login_manager
from flask_login import UserMixin


# -----------------------------
# ROLES
# -----------------------------
class Role(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50))


# -----------------------------
# USUARIOS
# -----------------------------
class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    email = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(255))

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    role = db.relationship("Role")

    incidents = db.relationship(
        "Incident",
        lazy=True
    )


# -----------------------------
# RECURSOS
# -----------------------------
class Resource(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50))


# -----------------------------
# TIPOS DE INCIDENCIA
# -----------------------------
class IncidentType(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))


# -----------------------------
# INCIDENCIAS
# -----------------------------
class Incident(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    start_date = db.Column(db.DateTime)

    end_date = db.Column(db.DateTime)

    address = db.Column(db.String(255))

    latitude = db.Column(db.Float)

    longitude = db.Column(db.Float)

    incidence = db.Column(db.Text)

    observations = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    incidentType_id = db.Column(db.Integer, db.ForeignKey('incident_type.id'))

    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'))

    # Relaciones

    user = db.relationship("User")

    incident_type = db.relationship("IncidentType")

    resource = db.relationship("Resource")


# -----------------------------
# FLASK LOGIN
# -----------------------------
@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))
