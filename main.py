import os
import logging
import requests
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    PreCheckoutQueryHandler
)

# ================== НАСТРОЙКИ ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден")
if not GROQ_API_KEY:
    raise RuntimeError("❌ GROQ_API_KEY не найден")
if not PAYMENT_PROVIDER_TOKEN:
    raise RuntimeError("❌ PAYMENT_PROVIDER_TOKEN не найден")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"  # актуальная, стабильная модель

FREE_LIMIT = 5          # сообщений в день
PREMIUM_DAYS = 30       # срок подписки
PRICE_KZT = 1990        # цена подписки

logging.basicConfig(level=logging.INFO)

# ================== ХРАНИЛИЩЕ ==================
USERS = {}  # user_id: {count, reset_at, premium_until}

# ================== GROQ ==================
def ask_groq(text: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "Ты профессиональный AI-консультант по бизнесу, крипто и технологиям."},
            {"role": "user", "content": text}
        ],
        "temperature": 0.7
    }

    r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# ================== ЛОГИКА ==================
def get_user(user_id: int):
    now = datetime.utcnow()
    user = USERS.get(user_id)

    if not user or user["reset_at"] < now:
        user = {
            "count": 0,
            "reset_at": now + timedelta(days=1),
            "premium_until": None
        }
        USERS[user_id] = user

    return user

def is_premium(user):
    return user["premium_until"] and user["premium_until"] > datetime.utcnow()

# ================== КОМАНДЫ ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 *AI-Консультант*\n\n"
        "🆓 Бесплатно: 5 сообщений в день\n"
        "💎 Premium: без лимитов + приоритет\n\n"
        "Напиши вопрос или оформи подписку 👇"
    )
    keyboard = [
        [InlineKeyboardButton("💎 Купить Premium", callback_data="buy")]
    ]
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== СООБЩЕНИЯ ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user = get_user(user_id)

    if not is_premium(user):
        if user["count"] >= FREE_LIMIT:
            await update.message.reply_text(
                "❌ Лимит бесплатных сообщений исчерпан.\n\n"
                "💎 Оформи Premium для безлимитного доступа."
            )
            return
        user["count"] += 1

    try:
        await update.message.chat.send_action("typing")
        answer = ask_groq(update.message.text)
        await update.message.reply_text(answer)
    except Exception as e:
        logging.exception(e)
        await update.message.reply_text("⚠️ Ошибка AI. Попробуй позже.")

# ================== ПОКУПКА ==================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    prices = [LabeledPrice("Premium подписка (30 дней)", PRICE_KZT * 100)]

    await query.message.reply_invoice(
        title="AI-Консультант Premium",
        description="Безлимитный доступ к AI на 30 дней",
        payload="premium_sub",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="KZT",
        prices=prices
    )

async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user = get_user(user_id)
    user["premium_until"] = datetime.utcnow() + timedelta(days=PREMIUM_DAYS)

    await update.message.reply_text(
        "✅ *Premium активирован!*\n\n"
        "Теперь у тебя безлимитный доступ 🎉",
        parse_mode="Markdown"
    )

# ================== MAIN ==================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
