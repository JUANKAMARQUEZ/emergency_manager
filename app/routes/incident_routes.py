from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_required, current_user
from datetime import datetime

from app.models import Incident, IncidentType, Resource
from app.extensions import db


incident_bp = Blueprint("incident", __name__)


# --------------------------------
# DASHBOARD
# --------------------------------
@incident_bp.route("/dashboard")
@login_required
def dashboard():

    total = Incident.query.count()

    active = Incident.query.filter_by(end_date=None).count()

    closed = Incident.query.filter(Incident.end_date != None).count()

    return render_template(
        "dashboard.html",
        total=total,
        active=active,
        closed=closed
    )


# --------------------------------
# LISTA DE INCIDENCIAS
# --------------------------------
@incident_bp.route("/incidents")
@login_required
def incidents():

    incidents = Incident.query.order_by(Incident.start_date.desc()).all()

    return render_template(
        "incidents/list.html",
        incidents=incidents
    )


# --------------------------------
# CREAR INCIDENCIA
# --------------------------------
@incident_bp.route("/incidents/create", methods=["GET","POST"])
@login_required
def create_incident():

    types = IncidentType.query.all()

    if request.method == "POST":

        incident = Incident(

            start_date=datetime.now(),

            address=request.form["address"],

            latitude=request.form["latitude"],

            longitude=request.form["longitude"],

            incidence=request.form["incidence"],

            incidentType_id=request.form["incident_type"],

            user_id=current_user.id
        )

        db.session.add(incident)

        db.session.commit()

        return redirect("/incidents")

    return render_template(
        "incidents/create.html",
        types=types
    )


# --------------------------------
# GESTIONAR INCIDENCIA
# --------------------------------
@incident_bp.route("/incidents/manage/<int:id>", methods=["GET","POST"])
@login_required
def manage_incident(id):

    incident = Incident.query.get(id)

    # -------------------------------
    # RECURSOS DISPONIBLES
    # -------------------------------

    busy_resources = db.session.query(Incident.resource_id)\
        .filter(Incident.end_date == None)\
        .filter(Incident.resource_id != None)\
        .all()

    busy_ids = [r[0] for r in busy_resources]

    resources = Resource.query.filter(~Resource.id.in_(busy_ids)).all()

    # Añadir el recurso actual
    if incident.resource_id:
        current_resource = Resource.query.get(incident.resource_id)
        if current_resource not in resources:
            resources.append(current_resource)

    # -------------------------------
    # POST
    # -------------------------------

    if request.method == "POST":

        action = request.form.get("action")

         # ✔ asignar / quitar recurso
        resource_id = request.form.get("resource")

        if resource_id:
             incident.resource_id = resource_id
        else:
            incident.resource_id = None

         # ✔ guardar observaciones SIEMPRE
        incident.observations = request.form["observations"]

         # ✔ finalizar incidencia
        if action == "finish":

          if not incident.observations:
             flash("Debes indicar una resolución", "danger")
             return redirect(request.url)

          incident.end_date = datetime.now()

        db.session.commit()

        return redirect("/incidents")
    # -------------------------------
    # GET
    # -------------------------------

    return render_template(
        "incidents/manage.html",
        incident=incident,
        resources=resources
    )
# ---------------------
# MAPA DE INCIDENCIAS
# ---------------------

@incident_bp.route("/map")
@login_required
def map_incidents():

    incidents = Incident.query.all()

    data = []

    for incident in incidents:

        if incident.latitude and incident.longitude:

            data.append({
                "id": incident.id,
                "address": incident.address,
                "incidence": incident.incidence,
                "latitude": incident.latitude,
                "longitude": incident.longitude,

                "type": incident.incident_type.name if incident.incident_type else "Otros",

                "resource": incident.resource.name if incident.resource else "Sin asignar",

                "resolution": incident.observations if incident.observations else "Pendiente",

                "status": "finalizada" if incident.end_date else "activa"
            })

    return render_template(
        "map.html",
        incidents=data
    )

# ---------------------------
# VER INCIDENCIAS FINALIZADAS
# ---------------------------

@incident_bp.route("/incidents/view/<int:id>")
@login_required
def view_incident(id):

    incident = Incident.query.get(id)

    duration = None

    if incident.end_date:

        delta = incident.end_date - incident.start_date

        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60

        partes = []

        if days:
            partes.append(f"{days} días")
        if hours:
            partes.append(f"{hours} horas")
        if minutes:
            partes.append(f"{minutes} minutos")

        duration = ", ".join(partes)

    return render_template(
        "incidents/view.html",
        incident=incident,
        duration=duration
    )
