import os
import json
import logging
import urllib.request
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ---------- CONFIG ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not BOT_TOKEN or not GROQ_API_KEY:
    raise RuntimeError("❌ BOT_TOKEN или GROQ_API_KEY не заданы")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

logging.basicConfig(level=logging.INFO)

# ---------- HANDLERS ----------
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Привет! Я AI-ассистент.\n"
        "Задай любой вопрос — отвечу 🤖"
    )

def ask_groq(prompt: str) -> str:
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Ты полезный и дружелюбный AI-ассистент."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    req = urllib.request.Request(
        GROQ_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]

def handle_message(update: Update, context: CallbackContext):
    user_text = update.message.text

    try:
        reply = ask_groq(user_text)
        update.message.reply_text(reply)
    except Exception as e:
        logging.exception("Groq error")
        update.message.reply_text("⚠️ Ошибка AI. Попробуй позже.")

# ---------- MAIN ----------
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    logging.info("🤖 AI Bot started (Groq)")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
