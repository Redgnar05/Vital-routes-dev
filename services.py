import requests
from datetime import datetime
from dotenv import load_dotenv
import os

# Cargar .env
load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
UNITS = os.getenv("UNITS", "metric")
LANG = os.getenv("LANG", "es")
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


# ============================================================
# OBTENER CLIMA DESDE API REAL
# ============================================================
def obtener_clima(ciudad: str):
    params = {
        "q": ciudad,
        "appid": WEATHER_API_KEY,
        "units": UNITS,
        "lang": LANG,
    }

    try:
        resp = requests.get(WEATHER_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        return {
            "ciudad": data.get("name", ciudad),
            "pais": data.get("sys", {}).get("country", ""),
            "temp": data["main"]["temp"],
            "sensacion": data["main"]["feels_like"],
            "humedad": data["main"]["humidity"],
            "descripcion": data["weather"][0]["description"].capitalize(),
        }

    except Exception as e:
        print("Error obteniendo clima:", e)
        return None


# ============================================================
# DATOS SIMULADOS (AIRE Y RUIDO)
# ============================================================
def obtener_calidad_aire_mock(ciudad: str):
    return {"pm25": 35, "pm10": 60, "aqi": 80, "categoria": "Moderada"}


def obtener_ruido_mock(ciudad: str):
    return {"ruido_db": 65, "fuente_probable": "Tráfico vehicular"}


# ============================================================
# CALCULAR RIESGO PERSONALIZADO DEL USUARIO
# ============================================================
def calcular_riesgo_salud(clima, aire, ruido, user):
    score = 0

    temp = clima["temp"]
    humedad = clima["humedad"]
    aqi = aire["aqi"]
    db = ruido["ruido_db"]

    # ----------------------------------------
    # 1) TEMPERATURA + SENSIBILIDADES
    # ----------------------------------------
    if temp < 5 or temp > 32:
        score += 3
    elif temp < 10 or temp > 28:
        score += 2

    if user.get("sensible_calor") == "Si" and temp > 28:
        score += 2

    if user.get("sensible_frio") == "Si" and temp < 10:
        score += 2

    # ----------------------------------------
    # 2) HUMEDAD
    # ----------------------------------------
    if humedad > 80:
        score += 1

    # ----------------------------------------
    # 3) CALIDAD DEL AIRE
    # ----------------------------------------
    if aqi <= 50:
        score += 0
    elif aqi <= 100:
        score += 1
    elif aqi <= 150:
        score += 3
    else:
        score += 5

    # Condiciones respiratorias
    if user.get("asma") == "Si" or user.get("respiratorio") == "Si":
        if aqi > 80:
            score += 3
        if aqi > 120:
            score += 5

    if user.get("alergias") == "Si" and aqi > 70:
        score += 2

    # ----------------------------------------
    # 4) RUIDO AMBIENTAL
    # ----------------------------------------
    if db > 80:
        score += 3
    elif db > 70:
        score += 2
    elif db > 60:
        score += 1

    if user.get("sensibilidad_ruido") == "Si" and db > 60:
        score += 2

    # ----------------------------------------
    # 5) SALUD GENERAL
    # ----------------------------------------
    if user.get("hipertension") == "Si":
        score += 2

    if user.get("diabetes") == "Si":
        score += 1

    edad = int(user.get("edad", 0) or 0)

    if edad >= 65:
        score += 3
    elif edad >= 50:
        score += 1

    # ----------------------------------------
    # 6) ACTIVIDAD FÍSICA
    # ----------------------------------------
    act = user.get("actividad")

    if act == "Alto" and (temp > 28 or temp < 10):
        score += 2

    if act == "Alto" and aqi > 100:
        score += 3

    # ----------------------------------------
    # 7) EXPOSICIÓN AL AIRE LIBRE
    # ----------------------------------------
    aire_libre = user.get("aire_libre")

    if aire_libre == "Más de 4h":
        score += 2
    elif aire_libre == "2-4h":
        score += 1

    # ----------------------------------------
    # CLASIFICACIÓN FINAL
    # ----------------------------------------
    if score <= 5:
        nivel = "Bajo"
        color = "verde"
    elif score <= 12:
        nivel = "Medio"
        color = "amarillo"
    else:
        nivel = "Alto"
        color = "rojo"

    return {"score": score, "nivel": nivel, "color": color}


# ============================================================
# GENERADOR DE RECOMENDACIONES PERSONALIZADAS
# ============================================================
def generar_recomendaciones(riesgo, clima, aire, ruido, user):
    recomendaciones = []
    temp = clima["temp"]
    aqi = aire["aqi"]
    db = ruido["ruido_db"]

    # ----------------------------------------
    # 1) BASE SEGÚN RIESGO
    # ----------------------------------------
    if riesgo["nivel"] == "Bajo":
        recomendaciones.append("Las condiciones son buenas para actividades al aire libre.")
    elif riesgo["nivel"] == "Medio":
        recomendaciones.append("Evita esfuerzos intensos y mantente hidratado.")
    else:
        recomendaciones.append("El riesgo es alto. Limita tu tiempo al aire libre.")

    # ----------------------------------------
    # 2) PERSONALIZADA POR CALOR/FRÍO
    # ----------------------------------------
    if temp > 30:
        recomendaciones.append("Evita el sol directo y toma agua frecuentemente.")
        if user.get("sensible_calor") == "Si":
            recomendaciones.append("Eres sensible al calor: evita salir entre 12:00 y 16:00.")

    if temp < 10:
        recomendaciones.append("Abrigarte bien si sales.")
        if user.get("sensible_frio") == "Si":
            recomendaciones.append("Tu sensibilidad al frío requiere salidas cortas.")

    # ----------------------------------------
    # 3) CALIDAD DEL AIRE
    # ----------------------------------------
    if aqi > 100:
        recomendaciones.append("Evita ejercicios intensos al aire libre por la contaminación.")

    if (user.get("asma") == "Si" or user.get("respiratorio") == "Si") and aqi > 80:
        recomendaciones.append("Usa cubrebocas al salir debido a tu condición respiratoria.")

    if user.get("alergias") == "Si" and aqi > 70:
        recomendaciones.append("El aire puede agravar tus alergias.")

    # ----------------------------------------
    # 4) RUIDO
    # ----------------------------------------
    if db > 70:
        recomendaciones.append("El ruido es alto. Prefiere rutas tranquilas.")

    if user.get("sensibilidad_ruido") == "Si":
        recomendaciones.append("Eres sensible al ruido: evita avenidas grandes.")

    # ----------------------------------------
    # 5) ACTIVIDAD FÍSICA Y TRANSPORTE
    # ----------------------------------------
    actividad = user.get("actividad")
    transporte = user.get("transporte")

    if actividad == "Alto" and (temp > 28 or aqi > 100):
        recomendaciones.append("Haz ejercicio en interiores hoy.")

    if transporte == "Caminata" and aqi > 120:
        recomendaciones.append("No es recomendable caminar por la contaminación.")

    if transporte == "Bicicleta" and db > 70:
        recomendaciones.append("Busca ciclovías menos ruidosas.")

    if transporte == "Transporte público" and aqi > 120:
        recomendaciones.append("Usa cubrebocas en el transporte público.")

    # ----------------------------------------
    # 6) HORARIO SUGERIDO
    # ----------------------------------------
    if riesgo["nivel"] == "Alto":
        sugerencia_horario = "Evita salir entre 11:00 y 17:00."
    elif riesgo["nivel"] == "Medio":
        sugerencia_horario = "Mejor salir antes de las 10:00 o después de las 18:00."
    else:
        sugerencia_horario = "Puedes salir a cualquier hora."

    return recomendaciones, sugerencia_horario
