import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# -------------------- ENV --------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден")
if not GROQ_API_KEY:
    raise RuntimeError("❌ GROQ_API_KEY не найден")

# -------------------- GROQ --------------------

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"  # стабильная модель

def ask_groq(user_text: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "Ты полезный и дружелюбный ассистент."},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.7,
        "max_tokens": 512,          # 🔥 ОБЯЗАТЕЛЬНО
        "top_p": 1,
        "stream": False
    }

    try:
        response = requests.post(
            GROQ_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            logging.error(f"GROQ STATUS {response.status_code}: {response.text}")
            return "⚠️ AI временно недоступен. Попробуй ещё раз."

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        logging.exception("GROQ ERROR")
        return "⚠️ Ошибка AI."

# -------------------- TELEGRAM --------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.chat.send_action("typing")

    reply = ask_groq(text)
    await update.message.reply_text(reply)

# -------------------- MAIN --------------------

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("✅ Бот запущен и готов")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
