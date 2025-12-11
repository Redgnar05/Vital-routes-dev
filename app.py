from flask import Flask, render_template
from dotenv import load_dotenv
import os

from db import init_db, mongo
from utils import usuario_logueado

# Rutas
from routes.auth_routes import init_auth_routes
from routes.dashboard_routes import init_dashboard_routes


def crear_app():

    load_dotenv()  # Cargar variables .env

    # Crear instancia de Flask
    app = Flask(__name__)

    # Cargar SECRET_KEY y MONGO_URI desde .env
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")

    # Inicializar base de datos
    init_db(app)

    # ======== RUTA HOME ========
    @app.route("/")
    def home():
        return render_template("index.html", logueado=usuario_logueado())

    # Registrar rutas modulares
    init_auth_routes(app)
    init_dashboard_routes(app)

    return app


if __name__ == "__main__":
    app = crear_app()
    app.run(debug=True)
