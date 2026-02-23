import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# -------------------------
# НАСТРОЙКИ
# -------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("❌ Переменная BOT_TOKEN не задана")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# -------------------------
# КОМАНДЫ БОТА
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 NurAgent запущен и работает!\n\n"
        "Доступные команды:\n"
        "/start — старт\n"
        "/report — публичный отчёт\n"
        "/help — помощь"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Помощь\n\n"
        "Этот бот — кооперативный AI-проект.\n"
        "Отчёт открыт для всех участников."
    )

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📊 ПУБЛИЧНЫЙ ОТЧЁТ\n\n"
        "💰 Общий доход: $0\n"
        "👥 Активных партнёров: 0\n\n"
        "📌 Распределение:\n"
        "• 70% — партнёрам\n"
        "• 10% — инвестиции\n"
        "• 10% — благотворительность\n"
        "• 10% — оплата сервисов\n\n"
        "⏱ Обновляется автоматически"
    )
    await update.message.reply_text(text)

# -------------------------
# ЗАПУСК
# -------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("report", report))

    logging.info("🚀 NurAgent bot started (polling)")
    app.run_polling()

if __name__ == "__main__":
    main()
