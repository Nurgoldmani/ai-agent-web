import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ---------- PUBLIC REPORT ----------
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

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.callback_query.message.reply_text(text, parse_mode="Markdown")


# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Добро пожаловать в *NurAgent*\n\n"
        "NurAgent — кооперативный AI-проект.\n"
        "Прозрачная модель, открытая отчётность,\n"
        "участие добровольное.\n\n"
        "Выберите действие 👇"
    )

    keyboard = [
        [InlineKeyboardButton("📊 Публичный отчёт", callback_data="public_report")],
        [InlineKeyboardButton("📜 Правила проекта", callback_data="rules")],
        [InlineKeyboardButton("🤝 Стать партнёром", callback_data="partner")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


# ---------- BUTTONS ----------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "public_report":
        await public_report(update, context)

    elif query.data == "rules":
        await query.message.reply_text(
            "📜 *Правила проекта*\n\n"
            "— участие добровольное\n"
            "— доход не гарантируется\n"
            "— распределение согласно README\n"
            "— проект находится в разработке",
            parse_mode="Markdown",
        )

    elif query.data == "partner":
        await query.message.reply_text(
            "🤝 *Стать партнёром*\n\n"
            "Партнёрство открыто.\n"
            "Следите за обновлениями или свяжитесь с администратором.\n\n"
            "_Автоматическая регистрация будет добавлена позже._",
            parse_mode="Markdown",
        )


# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("public_report", public_report))
    app.add_handler(CallbackQueryHandler(buttons))

    app.run_polling()


if __name__ == "__main__":
    main()
