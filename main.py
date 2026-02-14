import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

from openai import OpenAI

# ---------------- CONFIG ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not BOT_TOKEN or not GROQ_API_KEY:
    raise RuntimeError("BOT_TOKEN или GROQ_API_KEY не заданы в Variables")

# Groq (OpenAI-compatible)
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ---------------- HANDLERS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я AI-ассистент.\n\n"
        "Задай любой вопрос — я отвечу 🤖"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "Ты умный, дружелюбный AI-ассистент. Отвечай кратко и по делу."
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            temperature=0.7,
            max_tokens=500,
        )

        ai_reply = response.choices[0].message.content
        await update.message.reply_text(ai_reply)

    except Exception as e:
        logging.exception("Ошибка Groq")
        await update.message.reply_text(
            "⚠️ Произошла ошибка при обращении к AI. Попробуй позже."
        )

# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("🤖 AI Bot started. Polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
