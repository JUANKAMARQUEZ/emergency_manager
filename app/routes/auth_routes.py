from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash

from app.models import User

auth_bp = Blueprint("auth", __name__)


# -------------------------
# LOGIN
# -------------------------

@auth_bp.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        # 🔐 comprobar hash y estado de usuario
        if user and user.active and check_password_hash(user.password, password):

            login_user(user)

            next_page = request.args.get("next")

            return redirect(next_page or "/dashboard")
        
        elif user and not user.active:
            flash("Usuario inhabilitado", "danger")

        else:

            flash("Email o contraseña incorrectos", "danger")

    return render_template("login.html")


# -------------------------
# LOGOUT
# -------------------------

@auth_bp.route("/logout")
def logout():

    logout_user()

    return redirect("/")