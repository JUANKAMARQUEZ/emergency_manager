from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models import User, Role

user_bp = Blueprint("user", __name__)


# -------------------------
# PERFIL
# -------------------------


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    user = current_user

    if request.method == "POST":

        user.name = request.form["name"]

        # 🔐 cambiar contraseña si se introduce
        if request.form["password"]:

            current_password = request.form["current_password"]

            # 🔒 comprobar contraseña actual
            if not check_password_hash(user.password, current_password):

                flash("Debes introducir correctamente tu contraseña actual", "danger")

                return redirect(request.url)

            # 🔒 validar nueva contraseña
            if len(request.form["password"]) < 4:

                flash("La contraseña debe tener al menos 4 caracteres", "danger")

                return redirect(request.url)

            user.password = generate_password_hash(
                request.form["password"], method="pbkdf2:sha256"
            )

        db.session.commit()

        flash("Perfil actualizado correctamente", "success")

        return redirect("/dashboard")

    return render_template("profile.html", user=user)


# -------------------------
# LISTADO USUARIOS
# -------------------------


@user_bp.route("/users")
@login_required
def users():

    if current_user.role.name != "administrador":
        return redirect("/dashboard")

    users = User.query.all()

    return render_template("users.html", users=users)


# -------------------------
# CREAR USUARIO
# -------------------------


@user_bp.route("/users/create", methods=["GET", "POST"])
@login_required
def create_user():

    if current_user.role.name != "administrador":
        return redirect("/dashboard")

    roles = Role.query.all()

    if request.method == "POST":

        # 📧 comprobar email duplicado
        existing_user = User.query.filter_by(email=request.form["email"]).first()

        if existing_user:

            flash("El email ya está registrado", "danger")

            return redirect(request.url)

        # 🔒 validar contraseña
        if len(request.form["password"]) < 4:

            flash("La contraseña debe tener al menos 4 caracteres", "danger")

            return redirect(request.url)

        user = User(
            name=request.form["name"],
            email=request.form["email"],
            password=generate_password_hash(
                request.form["password"], method="pbkdf2:sha256"
            ),
            role_id=request.form["role"],
        )

        db.session.add(user)
        db.session.commit()

        flash("Usuario creado correctamente", "success")

        return redirect("/users")

    return render_template("user_form.html", roles=roles)


# -------------------------
# EDITAR USUARIO
# -------------------------


@user_bp.route("/users/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_user(id):

    if current_user.role.name != "administrador":
        return redirect("/dashboard")

    user = User.query.get(id)

    roles = Role.query.all()

    if request.method == "POST":

        # 🔒 impedir que el administrador
        # cambie su propia contraseña aquí

        if int(user.id) == int(current_user.id):

            flash("  Debes cambiar tu contraseña desde Mi perfil", "warning")

            return redirect("/profile")

        # 📧 comprobar email duplicado
        existing_user = User.query.filter_by(email=request.form["email"]).first()

        if existing_user and existing_user.id != user.id:

            flash("El email ya está registrado", "danger")
            return redirect("/users")

        user.name = request.form["name"]
        user.email = request.form["email"]
        user.role_id = request.form["role"]

        # 🔐 actualizar contraseña si se introduce
        if request.form["password"]:

            # 🔒 validar contraseña
            if len(request.form["password"]) < 4:

                flash("La contraseña debe tener al menos 4 caracteres", "danger")

                return redirect(request.url)

            user.password = generate_password_hash(
                request.form["password"], method="pbkdf2:sha256"
            )

        db.session.commit()

        flash("Usuario actualizado correctamente", "success")

        return redirect("/users")

    return render_template("user_form.html", user=user, roles=roles)


# -----------------------------------------
# ELIMINAR USUARIO (EN REALIDAD INHABILITAR)
# -----------------------------------------


@user_bp.route("/users/toggle/<int:id>")
@login_required
def toggle_user(id):

    if current_user.role.name != "administrador":
        return redirect("/dashboard")

    user = User.query.get(id)

    if not user:
        return redirect("/users")

    # ❌ evitar que el administrador inhabilite su propio usuario
    if int(user.id) == int(current_user.id):

        flash("No puedes inhabilitar tu propio usuario", "danger")

        return redirect("/users")

    # ❌ evitar inhabilitar último administrador
    if user.role.name == "administrador" and user.active:

        admins = User.query.filter_by(role_id=user.role_id, active=True).all()

        if len(admins) <= 1:

            flash("No puedes inhabilitar el último administrador", "danger")

            return redirect("/users")

    # Cambiar estado usuario
    user.active = not user.active

    db.session.commit()

    # Mensaje dinámico
    if user.active:

        flash("Usuario habilitado correctamente", "success")

    else:

        flash("Usuario inhabilitado correctamente", "warning")

    return redirect("/users")
