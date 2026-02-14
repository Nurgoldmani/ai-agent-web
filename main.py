import os
import time
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Бот запущен и работает 24/7!\n\nНапиши любое сообщение."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ты написал: {update.message.text}")

def main():
    if not BOT_TOKEN:
        raise RuntimeError("❌ BOT_TOKEN не найден")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("ping", start))
    app.add_handler(CommandHandler(None, echo))

    print("🤖 Bot started. Polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
