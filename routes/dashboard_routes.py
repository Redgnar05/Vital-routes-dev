from flask import render_template, request, redirect, url_for, session
from bson.objectid import ObjectId

from utils import usuario_logueado, requerir_login
from db import mongo
from services import (
    obtener_clima,
    obtener_calidad_aire_mock,
    obtener_ruido_mock,
    calcular_riesgo_salud,
    generar_recomendaciones
)


def init_dashboard_routes(app):

    @app.route("/dashboard", methods=["GET", "POST"])
    def dashboard():
        if not requerir_login():
            return redirect(url_for("login"))

        resultado = None
        error = None

        # Usuario siempre cargado
        user = mongo.db.usuarios.find_one({"_id": ObjectId(session["user_id"])})

        riesgo = None  # inicializado

        if request.method == "POST":
            ciudad = request.form.get("ciudad", "").strip()

            if not ciudad:
                error = "Ingresa una ciudad."
            else:
                clima = obtener_clima(ciudad)
                if not clima:
                    error = "No se pudo obtener el clima."
                else:
                    aire = obtener_calidad_aire_mock(ciudad)
                    ruido = obtener_ruido_mock(ciudad)

                    riesgo = calcular_riesgo_salud(clima, aire, ruido, user)

                    recomendaciones, sugerencia_horario = generar_recomendaciones(
                        riesgo, clima, aire, ruido, user
                    )

                    resultado = {
                        "ciudad": clima["ciudad"],
                        "clima": clima,
                        "aire": aire,
                        "ruido": ruido,
                        "riesgo": riesgo,
                        "recomendaciones": recomendaciones,
                        "sugerencia_horario": sugerencia_horario,
                    }

        return render_template(
            "dashboard.html",
            resultado=resultado,
            riesgo=riesgo,
            error=error,
            username=session.get("username"),
            logueado=usuario_logueado(),
            user=user
        )


    @app.route("/update_profile", methods=["GET", "POST"])
    def update_profile():
        if not requerir_login():
            return redirect(url_for("login"))

        user_id = session["user_id"]
        user = mongo.db.usuarios.find_one({"_id": ObjectId(user_id)})

        if request.method == "POST":
            datos = {
                "edad": request.form.get("edad"),
                "sexo": request.form.get("sexo"),

                "asma": "Si" if request.form.get("asma") else "No",
                "alergias": "Si" if request.form.get("alergias") else "No",
                "hipertension": "Si" if request.form.get("hipertension") else "No",
                "diabetes": "Si" if request.form.get("diabetes") else "No",
                "respiratorio": "Si" if request.form.get("respiratorio") else "No",

                "actividad": request.form.get("actividad"),
                "aire_libre": request.form.get("aire_libre"),

                "sensible_calor": "Si" if request.form.get("sensible_calor") else "No",
                "sensible_frio": "Si" if request.form.get("sensible_frio") else "No",
                "sensibilidad_ruido": "Si" if request.form.get("sensibilidad_ruido") else "No",
                "sensibilidad_contaminacion": "Si" if request.form.get("sensibilidad_contaminacion") else "No",

                "transporte": request.form.get("transporte"),
            }

            mongo.db.usuarios.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": datos}
            )

            user = mongo.db.usuarios.find_one({"_id": ObjectId(user_id)})

            return render_template(
                "update_profile.html",
                user=user,
                logueado=True,
                msg="¡Datos actualizados correctamente!"
            )

        return render_template(
            "update_profile.html",
            user=user,
            logueado=True
        )
