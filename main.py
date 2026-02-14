import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

# ===== ENV =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ===== GROQ FUNCTION =====
def ask_groq(user_text: str) -> str:
    if not GROQ_API_KEY:
        return "❌ GROQ_API_KEY не найден"

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Ты полезный AI-ассистент."},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Ошибка AI: {e}"

# ===== TELEGRAM HANDLER =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    reply = ask_groq(user_text)
    await update.message.reply_text(reply)

# ===== START APP =====
def main():
    if not BOT_TOKEN:
        raise RuntimeError("❌ BOT_TOKEN не найден")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
