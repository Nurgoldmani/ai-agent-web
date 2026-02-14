import os
import threading
import logging

from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --------------------
# LOGGING
# --------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# --------------------
# TELEGRAM BOT
# --------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Бот запущен и работает 24/7!\n\nНапиши любое сообщение."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🤖 Ты написал: {update.message.text}")

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🤖 Bot started. Polling...")
    app.run_polling()

# --------------------
# KEEPALIVE WEB SERVER (Railway)
# --------------------
web = Flask(__name__)

@web.route("/")
def home():
    return "Bot is alive", 200

def run_web():
    web.run(host="0.0.0.0", port=8080)

# --------------------
# START EVERYTHING
# --------------------
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    threading.Thread(target=run_web).start()
