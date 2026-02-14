import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ---------- НАСТРОЙКИ ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-3.5-turbo"

# ---------- ЛОГИ ----------
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---------- OPENROUTER ----------
def ask_ai(user_text: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://railway.app",
        "X-Title": "Telegram AI Bot"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Ты полезный и дружелюбный AI помощник."},
            {"role": "user", "content": user_text}
        ]
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            logging.error(f"OpenRouter error: {response.text}")
            return "⚠️ Ошибка AI. Попробуй позже."

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        logging.exception("AI exception")
        return "⚠️ Ошибка AI. Попробуй позже."

# ---------- ХЕНДЛЕРЫ ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я AI-бот.\n\nПросто напиши вопрос или сообщение."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.chat.send_action("typing")

    answer = ask_ai(user_text)
    await update.message.reply_text(answer)

# ---------- ЗАПУСК ----------
def main():
    if not BOT_TOKEN or not OPENROUTER_API_KEY:
        logging.error("❌ Не заданы BOT_TOKEN или OPENROUTER_API_KEY")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("🚀 Бот запущен")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
