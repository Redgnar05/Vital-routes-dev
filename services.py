import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
UNITS = os.getenv("UNITS", "metric")
LANG = os.getenv("LANG", "es")
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


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


def obtener_calidad_aire_mock(ciudad: str):
    return {"pm25": 35, "pm10": 60, "aqi": 80, "categoria": "Moderada"}


def obtener_ruido_mock(ciudad: str):
    return {"ruido_db": 65, "fuente_probable": "Tráfico vehicular"}


def calcular_riesgo_salud(clima, aire, ruido):
    score = 0
    temp = clima["temp"]

    if temp < 5 or temp > 32:
        score += 2
    elif temp < 10 or temp > 28:
        score += 1

    if clima["humedad"] > 80:
        score += 1

    aqi = aire["aqi"]
    if aqi > 150:
        score += 3
    elif aqi > 100:
        score += 2
    elif aqi > 50:
        score += 1

    db = ruido["ruido_db"]
    if db > 80:
        score += 3
    elif db > 70:
        score += 2
    elif db > 60:
        score += 1

    if score <= 2:
        return {"score": score, "nivel": "Bajo", "color": "verde"}
    elif score <= 5:
        return {"score": score, "nivel": "Medio", "color": "amarillo"}
    return {"score": score, "nivel": "Alto", "color": "rojo"}


def generar_recomendaciones(riesgo, clima, aire, ruido):
    recomendaciones = []

    if riesgo["nivel"] == "Bajo":
        recomendaciones.append("Las condiciones generales son favorables para actividades al aire libre.")
    elif riesgo["nivel"] == "Medio":
        recomendaciones.append("Evita esfuerzos físicos intensos.")
    else:
        recomendaciones.append("Permanece en interiores si es posible.")

    if aire["aqi"] > 100:
        recomendaciones.append("Restricción para personas con asma o problemas respiratorios.")

    if ruido["ruido_db"] > 70:
        recomendaciones.append("Elige rutas más tranquilas o usa protección auditiva.")

    ahora = datetime.now().hour
    sugerencia_horario = (
        "Antes de las 9:00 o después de las 18:00." if riesgo["nivel"] == "Alto"
        else "Evita el sol intenso entre 12:00 y 16:00."
    )

    return recomendaciones, sugerencia_horario
