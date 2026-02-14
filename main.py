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

# ======================
# НАСТРОЙКИ
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"

logging.basicConfig(level=logging.INFO)

# ======================
# GROQ AI
# ======================
def ask_groq(user_text: str) -> str:
    if not GROQ_API_KEY:
        return "❌ GROQ_API_KEY не найден."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    }

    r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)

    if r.status_code != 200:
        logging.error(f"GROQ ERROR {r.status_code}: {r.text}")
        return "⚠️ Ошибка AI. Попробуй позже."

    data = r.json()
    return data["choices"][0]["message"]["content"]


# ======================
# TELEGRAM HANDLER
# ======================
async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        answer = ask_groq(user_text)
    except Exception as e:
        logging.exception(e)
        answer = "⚠️ Внутренняя ошибка AI."

    await update.message.reply_text(answer)


# ======================
# START
# ======================
def main():
    if not BOT_TOKEN:
        raise RuntimeError("❌ BOT_TOKEN не найден")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    logging.info("🤖 Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
