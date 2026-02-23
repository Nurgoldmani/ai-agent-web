from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def public_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📊 *Публичный отчёт NurAgent*\n\n"
        "💰 Общий доход: $0\n"
        "👥 Активных партнёров: 0\n\n"
        "🔹 70% — партнёрам\n"
        "🔹 10% — инвестиционные проекты\n"
        "🔹 10% — благотворительность\n"
        "🔹 10% — поддержка сервиса\n\n"
        "_Проект работает по кооперативной модели._\n"
        "_Доход не гарантируется._"
    )

    await update.message.reply_text(text, parse_mode="Markdown")
