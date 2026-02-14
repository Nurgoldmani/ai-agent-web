import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from openai import OpenAI

# ---------- CONFIG ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not BOT_TOKEN or not GROQ_API_KEY:
    raise RuntimeError("❌ BOT_TOKEN или GROQ_API_KEY не заданы")

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

logging.basicConfig(level=logging.INFO)

# ---------- HANDLERS ----------
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Привет! Я AI-ассистент.\n\n"
        "Напиши любой вопрос — отвечу 🤖"
    )

def handle_message(update: Update, context: CallbackContext):
    user_text = update.message.text

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "Ты полезный и дружелюбный AI-ассистент."},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=500,
        )

        reply = response.choices[0].message.content
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

    logging.info("🤖 AI Bot started (polling)")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
