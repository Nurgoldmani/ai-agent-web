import os
import json
import urllib.request
from telegram.ext import Updater, MessageHandler, Filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def ask_groq(user_text):
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Ты полезный AI-помощник. Отвечай кратко и понятно."},
            {"role": "user", "content": user_text}
        ]
    }

    req = urllib.request.Request(
        GROQ_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]

def handle_message(update, context):
    text = update.message.text

    try:
        reply = ask_groq(text)
        update.message.reply_text(reply)
    except Exception as e:
        print("AI ERROR:", e)
        update.message.reply_text("⚠️ Ошибка AI. Попробуй позже.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
