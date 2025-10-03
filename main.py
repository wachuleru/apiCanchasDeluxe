from fastapi import FastAPI
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

app = FastAPI(title="API Canchas Deluxe")

# IDs de las canchas
canchas = {
    "cancha1": 5412,
    "cancha2": 1560,
    "cancha3": 1586
}

# Endpoint de reservas
url = "https://deluxesport.cl/wp-admin/admin-ajax.php"

# Traducción abreviada de días al español
dias_semana = {
    "Monday": "Lun",
    "Tuesday": "Mar",
    "Wednesday": "Mié",
    "Thursday": "Jue",
    "Friday": "Vie",
    "Saturday": "Sáb",
    "Sunday": "Dom"
}

# Cliente HTTP global
client = httpx.AsyncClient(timeout=15)

async def obtener_disponibilidad(fecha: datetime):
    year = fecha.year
    month = f"{fecha.month:02d}"
    day = f"{fecha.day:02d}"
    fecha_str = fecha.strftime("%Y-%m-%d")
    dia_abrev = dias_semana[fecha.strftime("%A")]

    resultado_dia = {
        "fecha": fecha_str,
        "dia": dia_abrev,
        "cancha1": [],
        "cancha2": [],
        "cancha3": []
    }

    for cancha, cancha_id in canchas.items():
        payload = (
            f"action=wc_appointments_get_slots&form="
            f"wc_appointments_field_start_date_month%3D{month}%26"
            f"wc_appointments_field_start_date_day%3D{day}%26"
            f"wc_appointments_field_start_date_year%3D{year}%26"
            f"wc_appointments_field_start_date_time%3D%26"
            f"wc_appointments_field_addons_duration%3D0%26"
            f"wc_appointments_field_addons_cost%3D0%26"
            f"add-to-cart%3D{cancha_id}%26"
            f"quantity%3D1&duration=0"
        )

        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://deluxesport.cl",
            "referer": "https://deluxesport.cl/product/cancha-3-football/",
            "user-agent": "Mozilla/5.0",
            "x-requested-with": "XMLHttpRequest"
        }

        try:
            response = await client.post(url, headers=headers, data=payload)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                slots = soup.select("ul.slot_column li.slot a")
                horas = [s.get("data-value") for s in slots] if slots else []
            else:
                horas = []
        except Exception:
            horas = []

        resultado_dia[cancha] = horas

    return resultado_dia

# ------------------- Endpoints -------------------

@app.get("/")
async def home():
    return {"mensaje": "Bienvenido a API Canchas Deluxe"}

@app.get("/semana")
async def disponibilidad_semana():
    fechas = [datetime.today() + timedelta(days=i) for i in range(7)]
    resultados = []
    for fecha in fechas:
        data = await obtener_disponibilidad(fecha)
        resultados.append(data)
    return resultados

@app.get("/dia/{fecha_str}")
async def disponibilidad_dia(fecha_str: str):
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    except ValueError:
        return {"error": "Formato de fecha inválido. Usa YYYY-MM-DD"}
    return await obtener_disponibilidad(fecha)
