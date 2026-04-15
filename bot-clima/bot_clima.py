import requests
from telegram import Bot
import time
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("API_KEY")
CIUDAD = "Madrid"

def obtener_clima():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CIUDAD}&appid={API_KEY}&units=metric&lang=es"
    respuesta = requests.get(url)
    datos = respuesta.json()

    clima = datos["weather"][0]["description"]
    viento = datos["wind"]["speed"]

    return clima, viento

def enviar_alerta(mensaje):
    bot = Bot(token=TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=mensaje)

def comprobar_clima():
    clima, viento = obtener_clima()

    if "lluvia" in clima.lower():
        enviar_alerta(f"🌧️ Va a llover hoy en {CIUDAD}")

    if viento > 10:
        enviar_alerta(f"💨 Mucho viento hoy en {CIUDAD}: {viento} m/s")

while True:
    comprobar_clima()
    time.sleep(3600)