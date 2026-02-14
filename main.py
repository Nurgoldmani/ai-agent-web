import os
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

TOKEN = os.getenv("BOT_TOKEN")

def start(update, context):
    update.message.reply_text(
        "👋 Бот запущен и работает 24/7!\n\nНапиши любое сообщение."
    )

def echo(update, context):
    text = update.message.text
    update.message.reply_text(f"Ты написал:\n{text}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling(drop_pending_updates=True)
    updater.idle()

if __name__ == "__main__":
    main()
