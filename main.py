import os
import requests
from telegram.ext import Updater, MessageHandler, Filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def ask_groq(prompt: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    r = requests.post(url, headers=headers, json=data, timeout=30)
    r.raise_for_status()

    return r.json()["choices"][0]["message"]["content"]

def handle(update, context):
    try:
        reply = ask_groq(update.message.text)
        update.message.reply_text(reply)
    except Exception as e:
        print("AI ERROR:", e)
        update.message.reply_text("⚠️ Ошибка AI. Попробуй позже.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
