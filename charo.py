import requests
import telebot
import pytz
import time  # Importar para añadir tiempos de espera
from datetime import datetime
from telebot import apihelper

# Lista de IDs de usuarios que han bloqueado el bot
blocked_users = ['1256474473']

def obtener_datos_meteorologicos(api_key, estacion_id, reintentos=3, espera=5):
    url = f"https://opendata.aemet.es/opendata/api/observacion/convencional/datos/estacion/{estacion_id}/"
    headers = {"Authorization": f"Bearer {api_key}"}

    for intento in range(reintentos):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                datos_url = response.json().get('datos', '')
                if datos_url:
                    data_response = requests.get(datos_url)
                    if data_response.status_code == 200:
                        datos_meteorologicos = data_response.json()
                        if datos_meteorologicos:
                            ultima_entrada = sorted(datos_meteorologicos, key=lambda x: x['fint'], reverse=True)[0]
                            return ultima_entrada
                        else:
                            return 'No hay datos disponibles.'
                    else:
                        return f'Error al recuperar datos: {data_response.status_code}'
                else:
                    return 'URL de datos no encontrada.'
            else:
                return f'Error: {response.status_code}'
        except requests.exceptions.RequestException as e:
            print(f"Intento {intento + 1} de {reintentos}: Error al conectar - {e}")
            if intento < reintentos - 1:
                time.sleep(espera)  # Esperar antes de intentar de nuevo
            else:
                return f"Error: No se pudo conectar después de {reintentos} intentos."

def enviar_datos_telegram(token, chat_id, datos, estacion_nombre):
    if chat_id in blocked_users:
        print(f"El usuario {chat_id} ha bloqueado el bot. No se enviará el mensaje.")
        return
    
    bot = telebot.TeleBot(token)
    if isinstance(datos, dict):
        utc_time = datetime.strptime(datos['fint'], '%Y-%m-%dT%H:%M:%S%z')
        local_time = utc_time.astimezone(pytz.timezone('Europe/Madrid'))

        mensaje = f'Datos de {estacion_nombre} - Hora Oficial (CET/CEST): {local_time.strftime("%Y-%m-%d %H:%M:%S")}\n'
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
                mensaje += f'{titulos[ind]}: {datos[ind]}\n'

        try:
            bot.send_message(chat_id, mensaje)
        except apihelper.ApiTelegramException as e:
            if e.result_json['description'] == 'Forbidden: bot was blocked by the user':
                print(f"Error: El bot fue bloqueado por el usuario {chat_id}. Añadiendo a la lista de bloqueados.")
                blocked_users.append(chat_id)
            else:
                print(f"Error: {e}")
    else:
        try:
            bot.send_message(chat_id, 'Error: ' + str(datos))
        except apihelper.ApiTelegramException as e:
            if e.result_json['description'] == 'Forbidden: bot was blocked by the user':
                print(f"Error: El bot fue bloqueado por el usuario {chat_id}. Añadiendo a la lista de bloqueados.")
                blocked_users.append(chat_id)
            else:
                print(f"Error: {e}")

def main():
    # Valores directos
    api_key = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJKNDk0OEBpY2xvdWQuY29tIiwianRpIjoiMDU4ZDJiNzAtNGJiNC00MWE2LTk1MzEtZmJmOWZhY2M5NmRjIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3MTMyNDM4ODUsInVzZXJJZCI6IjA1OGQyYjcwLTRiYjQtNDFhNi05NTMxLWZiZjlmYWNjOTZkYyIsInJvbGUiOiIifQ.2QEECrTNbTmbBBo3hQCrI1sXu8Q8rHxUzT4q_-kfwxE'
    token = '6659256025:AAFK3y_PbW3zhGzURyEc9v-7cZ1v9LwvNpc'
    chat_ids = ['317007077', '1256474473']  # Lista de chat IDs

    estaciones = {
        'Bilbao': '1082',
        'Mayorga': '2664B',
        'Ayamonte': '4642E'
    }

    for nombre, estacion_id in estaciones.items():
        datos_meteorologicos = obtener_datos_meteorologicos(api_key, estacion_id)
        for chat_id in chat_ids:
            enviar_datos_telegram(token, chat_id, datos_meteorologicos, nombre)

if __name__ == '__main__':
    main()
