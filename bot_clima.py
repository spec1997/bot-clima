import requests
from telegram import Bot
from telegram.error import TelegramError
import os
import sys

# ══════════════════════════════════════════════
#  CONFIGURACIÓN — todo por GitHub Secrets
# ══════════════════════════════════════════════
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("API_KEY")
CIUDAD = os.getenv("CIUDAD", "Madrid")

UMBRAL_VIENTO = float(os.getenv("UMBRAL_VIENTO", 10))
UMBRAL_TEMP_ALTA = float(os.getenv("UMBRAL_TEMP_ALTA", 38))
UMBRAL_TEMP_BAJA = float(os.getenv("UMBRAL_TEMP_BAJA", 2))

# ══════════════════════════════════════════════
#  FUNCIONES
# ══════════════════════════════════════════════

def verificar_config():
    faltantes = []
    if not TOKEN:    faltantes.append("TOKEN")
    if not CHAT_ID:  faltantes.append("CHAT_ID")
    if not API_KEY:  faltantes.append("API_KEY")
    if faltantes:
        print(f"❌ Faltan secrets en GitHub: {', '.join(faltantes)}")
        sys.exit(1)


def obtener_clima_actual():
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={CIUDAD}&appid={API_KEY}&units=metric&lang=es"
    )
    respuesta = requests.get(url, timeout=10)
    respuesta.raise_for_status()
    datos = respuesta.json()

    return {
        "descripcion": datos["weather"][0]["description"],
        "temp": datos["main"]["temp"],
        "sensacion": datos["main"]["feels_like"],
        "humedad": datos["main"]["humidity"],
        "viento": datos["wind"]["speed"],
    }


def obtener_pronostico():
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={CIUDAD}&appid={API_KEY}&units=metric&lang=es&cnt=4"
    )
    respuesta = requests.get(url, timeout=10)
    respuesta.raise_for_status()
    datos = respuesta.json()

    for bloque in datos["list"]:
        desc = bloque["weather"][0]["description"].lower()
        if any(p in desc for p in ["lluvia", "llovizna", "tormenta", "chubasco"]):
            return True
    return False


def enviar_mensaje(mensaje):
    try:
        bot = Bot(token=TOKEN)
        bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode="HTML")
        print(f"✅ Mensaje enviado")
    except TelegramError as e:
        print(f"❌ Error al enviar mensaje: {e}")
        raise


def comprobar_y_alertar():
    clima = obtener_clima_actual()
    alertas = []

    if obtener_pronostico():
        alertas.append("🌧️ <b>Lluvia prevista</b> en las próximas horas")

    if clima["viento"] > UMBRAL_VIENTO:
        alertas.append(f"💨 <b>Viento fuerte:</b> {clima['viento']} m/s")

    if clima["temp"] > UMBRAL_TEMP_ALTA:
        alertas.append(f"🔥 <b>Calor extremo:</b> {clima['temp']}°C")
    elif clima["temp"] < UMBRAL_TEMP_BAJA:
        alertas.append(f"🥶 <b>Frío intenso:</b> {clima['temp']}°C")

    if alertas:
        cabecera = f"⚠️ <b>Alerta clima en {CIUDAD}</b>\n"
        resumen = f"\n📍 Ahora: {clima['descripcion']}, {clima['temp']}°C (sensación {clima['sensacion']}°C)\n"
        mensaje = cabecera + resumen + "\n".join(alertas)
        enviar_mensaje(mensaje)
    else:
        print(f"☀️ Todo tranquilo en {CIUDAD}: {clima['descripcion']}, {clima['temp']}°C")


# ══════════════════════════════════════════════
#  EJECUCIÓN ÚNICA — GitHub Actions lanza esto cada hora
# ══════════════════════════════════════════════

if __name__ == "__main__":
    verificar_config()
    print(f"🤖 Comprobando clima en {CIUDAD}...")
    try:
        comprobar_y_alertar()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)