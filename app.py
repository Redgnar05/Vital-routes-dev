from flask import Flask, render_template
from dotenv import load_dotenv
import os

from db import mongo
from utils import usuario_logueado

from routes.auth_routes import init_auth_routes
from routes.dashboard_routes import init_dashboard_routes


def crear_app():

    load_dotenv()  # Cargar claves del archivo .env

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")

    mongo.init_app(app)


    @app.route("/")
    def home():
        return render_template("index.html", logueado=usuario_logueado())


    # Registrar rutas
    init_auth_routes(app)
    init_dashboard_routes(app)

    return app


if __name__ == "__main__":
    app = crear_app()
    app.run()
