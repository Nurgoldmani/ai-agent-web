import os
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def ask_groq(text: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Ты полезный AI ассистент."},
            {"role": "user", "content": text}
        ],
        "temperature": 0.7
    }

    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("AI ERROR:", e)
        return "⚠️ Ошибка AI. Попробуй позже."


def handle_message(update: Update, context: CallbackContext):
    user_text = update.message.text
    reply = ask_groq(user_text)
    update.message.reply_text(reply)


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("🤖 Bot started")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
