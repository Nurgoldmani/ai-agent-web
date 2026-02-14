import os
from telegram.ext import Updater, MessageHandler, Filters
from groq import Groq

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def handle_message(update, context):
    user_text = update.message.text

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Ты полезный AI-помощник. Отвечай кратко и понятно."},
                {"role": "user", "content": user_text}
            ]
        )

        reply = completion.choices[0].message.content
        update.message.reply_text(reply)

    except Exception as e:
        print("GROQ ERROR:", e)
        update.message.reply_text("⚠️ Ошибка AI. Попробуй позже.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
