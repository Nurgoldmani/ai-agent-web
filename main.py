import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)
from groq import Groq

# ================== НАСТРОЙКИ ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = "llama-3.1-8b-instant"

SYSTEM_PROMPT = (
    "Ты умный, вежливый и дружелюбный AI-ассистент. "
    "Всегда отвечай на РУССКОМ языке. "
    "Отвечай ясно, полезно и по делу."
)
# ===============================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден")

if not GROQ_API_KEY:
    raise RuntimeError("❌ GROQ_API_KEY не найден")

groq_client = Groq(api_key=GROQ_API_KEY)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋\n\n"
        "Я AI-бот и готов помочь тебе.\n"
        "Просто напиши свой вопрос ✨"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=0.7,
            max_tokens=700,
        )

        answer = response.choices[0].message.content
        await update.message.reply_text(answer)

    except Exception as e:
        logging.error(f"Groq error: {e}")
        await update.message.reply_text(
            "⚠️ Ошибка AI. Попробуй позже."
        )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("🤖 Бот запущен (Groq, polling)")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
