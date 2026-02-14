import os
import logging
import requests

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

# -------------------- НАСТРОЙКИ --------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

# -------------------- ПРОВЕРКИ --------------------

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден")

if not GROQ_API_KEY:
    raise RuntimeError("❌ GROQ_API_KEY не найден")

# -------------------- ЛОГИ --------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# -------------------- GROQ --------------------

def ask_groq(text: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": "Ты полезный и понятный AI-помощник."},
                {"role": "user", "content": text},
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }

        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()

        data = r.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        logging.error(f"GROQ ERROR: {e}")
        return "⚠️ Ошибка AI. Попробуй ещё раз позже."

# -------------------- TELEGRAM --------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    await update.message.chat.send_action("typing")

    answer = ask_groq(user_text)

    await update.message.reply_text(answer)

# -------------------- MAIN --------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("✅ Бот запущен и готов к работе")

    app.run_polling()

if __name__ == "__main__":
    main()
