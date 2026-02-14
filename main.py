import os
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler

# ========================
# CONFIG
# ========================
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"

# ========================
# TELEGRAM HANDLERS
# ========================
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Бот запущен и работает 24/7!\n\nНапиши любое сообщение."
    )

def handle_message(update: Update, context: CallbackContext):
    user_text = update.message.text

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Ты умный и дружелюбный AI помощник."},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
        data = response.json()

        reply = data["choices"][0]["message"]["content"]
        update.message.reply_text(reply)

    except Exception as e:
        update.message.reply_text("⚠️ Ошибка AI. Попробуй позже.")

# ========================
# KEEP-ALIVE WEB SERVER
# ========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive", 200

# ========================
# MAIN
# ========================
def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
