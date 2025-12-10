from flask import render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from db import mongo
from utils import usuario_logueado


def init_auth_routes(app):

    @app.route("/register", methods=["GET", "POST"])
    def register():
        error = None

        if request.method == "POST":
            username = request.form.get("username").strip()
            password = request.form.get("password").strip()

            if not username or not password:
                error = "Usuario y contraseña son obligatorios."
            else:
                existing = mongo.db.usuarios.find_one({"username": username})
                if existing:
                    error = "Ese usuario ya existe."
                else:
                    hash_pw = generate_password_hash(password)
                    mongo.db.usuarios.insert_one({
                        "username": username,
                        "password_hash": hash_pw,
                        "created_at": datetime.utcnow(),
                    })
                    return redirect(url_for("login"))

        return render_template("register.html", error=error, logueado=usuario_logueado())

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None

        if request.method == "POST":
            username = request.form.get("username").strip()
            password = request.form.get("password").strip()

            user = mongo.db.usuarios.find_one({"username": username})

            if user and check_password_hash(user["password_hash"], password):
                session["user_id"] = str(user["_id"])
                session["username"] = user["username"]
                return redirect(url_for("dashboard"))
            else:
                error = "Usuario o contraseña incorrectos."

        return render_template("login.html", error=error, logueado=usuario_logueado())

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("home"))
