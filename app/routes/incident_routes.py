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

    closed = Incident.query.filter(
        Incident.end_date.is_not(None)
    ).count()

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

    # Obtener incidencia o devolver error 404
    incident = Incident.query.get_or_404(id)

    # -------------------------------
    # RECURSOS DISPONIBLES
    # -------------------------------

    active_incidents = Incident.query.filter(
    Incident.end_date.is_(None),
    Incident.id != incident.id
    ).all()

    busy_ids = []

    for active_incident in active_incidents:

         for resource in active_incident.resources:

             busy_ids.append(resource.id)

    resources = Resource.query.filter(
            ~Resource.id.in_(busy_ids)
        ).all()

    # Añadir recursos actuales de la incidencia
    for resource in incident.resources:

     if resource not in resources:

        resources.append(resource)

    # -------------------------------
    # POST
    # -------------------------------

    if request.method == "POST":

        action = request.form.get("action")

        # ✔ múltiples recursos
        resource_ids = request.form.getlist("resources[]")

        selected_resources = []

        for resource_id in resource_ids:

            resource = Resource.query.get(resource_id)

            # Validar existencia
            if not resource:

                flash(
                "Uno de los recursos no existe",
                "danger"
                )

                return redirect(request.url)

            # Validar recurso ocupado
            busy_incident = Incident.query.join(
                Incident.resources
            ).filter(
                Resource.id == resource.id,
                Incident.end_date.is_(None)
            ).first()

            if busy_incident and busy_incident.id != incident.id:

                flash(
                    f"El recurso {resource.name} ya está asignado",
                    "danger"
                )

                return redirect(request.url)

            

            selected_resources.append(resource)

        # Asignar recursos
        incident.resources = selected_resources

        # ✔ guardar observaciones
        incident.observations = request.form.get("observations")

        # ✔ finalizar incidencia
        if action == "finish":

            if not incident.observations:

                flash(
                "Debes indicar una resolución",
                "danger"
                )

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

                "resource": ", ".join(
                    [r.name for r in incident.resources]
                ) if incident.resources else "Sin asignar",

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

    incident = Incident.query.get_or_404(id)

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
