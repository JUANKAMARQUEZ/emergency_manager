from email.mime import message

from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_required, current_user
from math import radians, cos, sin, sqrt, atan2
from app.models import Incident, IncidentType, Resource
from app.extensions import db
from datetime import datetime

incident_bp = Blueprint("incident", __name__)

# --------------------------------
# FUNCION PARA CALCULAR DISTANCIA ENTRE COORDENADAS GEOGRÁFICAS
# --------------------------------


def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# --------------------------------
# FUNCIÓN PARA OBTENER RECURSO MÁS CERCANO
# --------------------------------


def get_nearest_resource(prefix, latitude, longitude):

    nearest_resource = None

    min_distance = 999999

    resources = Resource.query.filter(Resource.name.like(f"{prefix}-%")).all()

    for resource in resources:

        if not resource.latitude or not resource.longitude:
            continue

        # Ignorar recursos ocupados
        busy_incident = (
            Incident.query.join(Incident.resources)
            .filter(Resource.id == resource.id, Incident.end_date.is_(None))
            .first()
        )

        if busy_incident:
            continue

        distance = calculate_distance(
            float(latitude), float(longitude), resource.latitude, resource.longitude
        )

        if distance < min_distance:

            min_distance = distance

            nearest_resource = resource

    return nearest_resource, round(min_distance, 2)


# --------------------------------
# DASHBOARD
# --------------------------------
@incident_bp.route("/dashboard")
@login_required
def dashboard():

    total = Incident.query.count()

    active = Incident.query.filter_by(end_date=None).count()

    closed = Incident.query.filter(Incident.end_date.is_not(None)).count()

    return render_template("dashboard.html", total=total, active=active, closed=closed)


# --------------------------------
# LISTA DE INCIDENCIAS
# --------------------------------
@incident_bp.route("/incidents")
@login_required
def incidents():

    incidents = Incident.query.order_by(Incident.start_date.desc()).all()

    return render_template("incidents/list.html", incidents=incidents)


# --------------------------------
# CREAR INCIDENCIA
# --------------------------------
@incident_bp.route("/incidents/create", methods=["GET", "POST"])
@login_required
def create_incident():

    types = IncidentType.query.all()

    main_resource = None
    support_resource = None

    main_distance = None
    support_distance = None

    if request.method == "POST":

        address = request.form["address"]

        latitude = request.form["latitude"]

        longitude = request.form["longitude"]

        # Validar que se han obtenido coordenadas válidas
        if not latitude or not longitude:

            flash(
                 "Debes buscar una dirección válida antes de crear la incidencia",
                 "danger"
            )

            return redirect("/incidents/create")

        incidence = request.form["incidence"]

        incident_type_id = request.form["incident_type"]

        # Obtener tipo incidencia
        incident_type = IncidentType.query.get(incident_type_id)

        # 🚒 INCENDIO
        if incident_type.name == "Incendio":

            main_resource, main_distance = get_nearest_resource(
                "B", latitude, longitude
            )

            support_resource, support_distance = get_nearest_resource(
                "P", latitude, longitude
            )

        # 🚑 SANITARIA / SINIESTRO
        elif incident_type.name in ["Asistencia Sanitaria", "Siniestro Vial"]:

            main_resource, main_distance = get_nearest_resource(
                "A", latitude, longitude
            )

            support_resource, support_distance = get_nearest_resource(
                "P", latitude, longitude
            )

        # 🚓 RESTO
        else:

            main_resource, main_distance = get_nearest_resource(
                "P", latitude, longitude
            )

        # Crear incidencia
        incident = Incident(
            address=address,
            latitude=latitude,
            longitude=longitude,
            incidence=incidence,
            start_date=datetime.now(),
            user_id=current_user.id,
            incidentType_id=incident_type_id,
        )

        db.session.add(incident)

        message = ""

        if main_resource:

            message += (
                f"Recurso principal sugerido: "
                f"{main_resource.name}"
                f" ({main_distance} km)"
            )

        if support_resource:

            message += (
                f" | Policía apoyo sugerida: "
                f"{support_resource.name}"
                f" ({support_distance} km)"
            )

        flash(message, "info")

        db.session.commit()

        flash("Incidencia creada correctamente", "success")

        return redirect("/incidents")

    return render_template(
        "incidents/create.html",
        types=types,
        main_resource=main_resource,
        main_distance=main_distance,
        support_resource=support_resource,
        support_distance=support_distance,
    )


# --------------------------------
# GESTIONAR INCIDENCIA
# --------------------------------
@incident_bp.route("/incidents/manage/<int:id>", methods=["GET", "POST"])
@login_required
def manage_incident(id):

    # Obtener incidencia o devolver error 404
    incident = Incident.query.get_or_404(id)

    main_resource = None
    support_resource = None

    main_distance = None
    support_distance = None

    # Solo sugerir si no hay recursos asignados
    if not incident.resources:

        # 🚒 INCENDIO
        if incident.incident_type.name == "Incendio":

            main_resource, main_distance = get_nearest_resource(
                "B", incident.latitude, incident.longitude
            )

            support_resource, support_distance = get_nearest_resource(
                "P", incident.latitude, incident.longitude
            )

        # 🚑 SANITARIA / SINIESTRO
        elif incident.incident_type.name in ["Asistencia Sanitaria", "Siniestro Vial"]:

            main_resource, main_distance = get_nearest_resource(
                "A", incident.latitude, incident.longitude
            )

            support_resource, support_distance = get_nearest_resource(
                "P", incident.latitude, incident.longitude
            )

        # 🚓 RESTO
        else:

            main_resource, main_distance = get_nearest_resource(
                "P", incident.latitude, incident.longitude
            )

    # -------------------------------
    # RECURSOS DISPONIBLES
    # -------------------------------

    active_incidents = Incident.query.filter(
        Incident.end_date.is_(None), Incident.id != incident.id
    ).all()

    busy_ids = []

    for active_incident in active_incidents:

        for resource in active_incident.resources:

            busy_ids.append(resource.id)

    resources = Resource.query.filter(~Resource.id.in_(busy_ids)).all()

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

                flash("Uno de los recursos no existe", "danger")

                return redirect(request.url)

            # Validar recurso ocupado
            busy_incident = (
                Incident.query.join(Incident.resources)
                .filter(Resource.id == resource.id, Incident.end_date.is_(None))
                .first()
            )

            if busy_incident and busy_incident.id != incident.id:

                flash(f"El recurso {resource.name} ya está asignado", "danger")

                return redirect(request.url)

            selected_resources.append(resource)

        # Asignar recursos
        incident.resources = selected_resources

        # ✔ guardar observaciones
        incident.observations = request.form.get("observations")

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

    resources_data = []

    all_resources = Resource.query.all()

    for resource in all_resources:

        busy_incident = (
            Incident.query.join(Incident.resources)
            .filter(Resource.id == resource.id, Incident.end_date.is_(None))
            .first()
        )

        resources_data.append(
            {
                "id": resource.id,
                "name": resource.name,
                "latitude": resource.latitude,
                "longitude": resource.longitude,
                "busy": True if busy_incident else False,
            }
        )
    return render_template(
        "incidents/manage.html",
        incident=incident,
        resources=resources,
        main_resource=main_resource,
        main_distance=main_distance,
        support_resource=support_resource,
        support_distance=support_distance,
        resources_map=resources_data,
    )


# ---------------------
# MAPA DE INCIDENCIAS
# ---------------------


@incident_bp.route("/map")
@login_required
def map_incidents():

    incidents = Incident.query.all()

    data = []
    resources_data = []

    for incident in incidents:

        if incident.latitude and incident.longitude:

            data.append(
                {
                    "id": incident.id,
                    "address": incident.address,
                    "incidence": incident.incidence,
                    "latitude": incident.latitude,
                    "longitude": incident.longitude,
                    "type": (
                        incident.incident_type.name
                        if incident.incident_type
                        else "Otros"
                    ),
                    "resource": (
                        ", ".join([r.name for r in incident.resources])
                        if incident.resources
                        else "Sin asignar"
                    ),
                    "resolution": (
                        incident.observations if incident.observations else "Pendiente"
                    ),
                    "status": "finalizada" if incident.end_date else "activa",
                }
            )

    resources = Resource.query.all()

    for resource in resources:

        busy_incident = (
            Incident.query.join(Incident.resources)
            .filter(Resource.id == resource.id, Incident.end_date.is_(None))
            .first()
        )

        resources_data.append(
            {
                "id": resource.id,
                "name": resource.name,
                "latitude": resource.latitude,
                "longitude": resource.longitude,
                "busy": True if busy_incident else False,
            }
        )

    return render_template("map.html", incidents=data, resources=resources_data)


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

    return render_template("incidents/view.html", incident=incident, duration=duration)
