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

        if request.method == "POST":
            ciudad = request.form.get("ciudad").strip()
            if ciudad:
                clima = obtener_clima(ciudad)
                if clima:
                    aire = obtener_calidad_aire_mock(ciudad)
                    ruido = obtener_ruido_mock(ciudad)
                    riesgo = calcular_riesgo_salud(clima, aire, ruido)
                    recomendaciones, sugerencia_horario = generar_recomendaciones(
                        riesgo, clima, aire, ruido
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
                else:
                    error = "No se pudo obtener el clima."
            else:
                error = "Ingresa una ciudad."

        return render_template(
            "dashboard.html",
            resultado=resultado,
            error=error,
            username=session.get("username"),
            logueado=usuario_logueado(),
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
                "respiratorio": "Si" if request.form.get("respiratorio") else "No",
                "actividad": request.form.get("actividad"),
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
