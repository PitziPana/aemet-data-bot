import os
import requests
import telebot
import pytz
from datetime import datetime

def obtener_datos_meteorologicos(api_key, estacion_id):
    url = f"https://opendata.aemet.es/opendata/api/observacion/convencional/datos/estacion/{estacion_id}/"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        datos_url = response.json().get('datos', '')
        if datos_url:
            data_response = requests.get(datos_url)
            if data_response.status_code == 200:
                datos_meteorologicos = data_response.json()
                # Retorna solo la última entrada, ya ajustada la hora
                if datos_meteorologicos:
                    ultima_entrada = sorted(datos_meteorologicos, key=lambda x: x['fint'], reverse=True)[0]
                    return ultima_entrada
                else:
                    return "No hay datos disponibles."
            else:
                return f"Error al recuperar datos: {data_response.status_code}"
        else:
            return "URL de datos no encontrada."
    else:
        return f"Error: {response.status_code}"

def enviar_datos_telegram(token, chat_id, datos, estacion_nombre):
    bot = telebot.TeleBot(token)
    if isinstance(datos, dict):  # Asegúrate de que los datos son un diccionario
        utc_time = datetime.strptime(datos['fint'], '%Y-%m-%dT%H:%M:%S%z')
        local_time = utc_time.astimezone(pytz.timezone('Europe/Madrid'))  # Convertir a hora local de Madrid

        mensaje = f"Datos de {estacion_nombre} - Hora Oficial (CET/CEST): {local_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        titulos = {
            'ta': 'Temperatura Ambiente (°C)',
            'prec': 'Precipitación (mm)',
            'vv': 'Velocidad del Viento (m/s)',
            'dv': 'Dirección del Viento (grados)',
            'hr': 'Humedad Relativa (%)',
            'pres': 'Presión Atmosférica (hPa)',
            'inso': 'Irradiación Solar (W/m²)'
        }
        indicadores_seleccionados = ['ta', 'prec', 'vv', 'dv', 'hr', 'pres', 'inso']
        for ind in indicadores_seleccionados:
            if ind in datos:
                mensaje += f"{titulos[ind]}: {datos[ind]}\n"

        bot.send_message(chat_id, mensaje)
    else:
        bot.send_message(chat_id, "Error: " + str(datos))

def main():
    api_key = os.getenv('API_KEY')
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    # Imprimir las variables de entorno para depuración (eliminar estas líneas en producción)
    print(f"API_KEY: {api_key}")
    print(f"TELEGRAM_TOKEN: {token}")
    print(f"TELEGRAM_CHAT_ID: {chat_id}")

    estaciones = {
        'Bilbao': '1082',
        'Mayorga': '2664B',
        'Ayamonte': '4642E'
    }

    for nombre, estacion_id in estaciones.items():
        datos_meteorologicos = obtener_datos_meteorologicos(api_key, estacion_id)
        enviar_datos_telegram(token, chat_id, datos_meteorologicos, nombre)

if __name__ == "__main__":
    main()
