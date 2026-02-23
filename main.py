import os
from fastapi import FastAPI, Request
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://xxx.up.railway.app

app = FastAPI()
tg_app = Application.builder().token(BOT_TOKEN).build()

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
        "_Проект работает по кооперативной модели._"
    )

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.callback_query.message.reply_text(text, parse_mode="Markdown")

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Публичный отчёт", callback_data="public_report")],
        [InlineKeyboardButton("📜 Правила", callback_data="rules")],
        [InlineKeyboardButton("🤝 Партнёрство", callback_data="partner")],
    ]

    await update.message.reply_text(
        "👋 *NurAgent*\n\nКооперативный AI-проект.\nВыберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

# ---------- BUTTONS ----------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "public_report":
        await public_report(update, context)

    elif q.data == "rules":
        await q.message.reply_text("📜 Правила см. в README.")

    elif q.data == "partner":
        await q.message.reply_text("🤝 Напишите администратору.")

# ---------- TELEGRAM ROUTES ----------
@app.on_event("startup")
async def on_startup():
    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CommandHandler("public_report", public_report))
    tg_app.add_handler(CallbackQueryHandler(buttons))

    await tg_app.initialize()
    await tg_app.bot.set_webhook(f"{WEBHOOK_URL}/telegram")
    await tg_app.start()

@app.post("/telegram")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, tg_app.bot)
    await tg_app.process_update(update)
    return {"ok": True}

@app.get("/")
def root():
    return {"status": "NurAgent online"}
