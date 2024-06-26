import os
import telebot

def enviar_datos_telegram(token, chat_id):
    bot = telebot.TeleBot(token)
    mensaje = "Mensaje de prueba desde GitHub Actions"
    bot.send_message(chat_id, mensaje)

def main():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    # Imprimir las variables de entorno para depuración
    print(f"TELEGRAM_TOKEN: {token}")
    print(f"TELEGRAM_CHAT_ID: {chat_id}")

    enviar_datos_telegram(token, chat_id)

if __name__ == "__main__":
    main()
