import os
import logging
import requests
from collections import defaultdict, deque
from datetime import date

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

# ================== НАСТРОЙКИ ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

FREE_LIMIT = 5  # бесплатные сообщения в день

# ================== ПРОВЕРКИ ==================

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден")
if not GROQ_API_KEY:
    raise RuntimeError("❌ GROQ_API_KEY не найден")

# ================== ЛОГИ ==================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# ================== ПАМЯТЬ ==================

user_memory = defaultdict(lambda: deque(maxlen=6))

# ================== ЛИМИТЫ ==================

user_usage = defaultdict(lambda: {"date": date.today(), "count": 0})
premium_users = set()  # позже подключим оплату

# ================== SYSTEM PROMPT ==================

SYSTEM_PROMPT = """
You are an AI Web3 & Crypto Assistant.

Your mission:
- Explain cryptocurrency, blockchain, Web3, AI agents, DeFi in simple language
- Help users understand real ways to earn in crypto and AI ecosystems
- Give structured, step-by-step answers
- Focus on practical tools and strategies
- Avoid hype, scams, and vague advice

Rules:
- If a question is not related to crypto, Web3, AI, or earning online — politely redirect
- Do not give financial guarantees
- Be clear, professional, and helpful
"""

# ================== GROQ ==================

def ask_groq(user_id: int, user_text: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(user_memory[user_id])
    messages.append({"role": "user", "content": user_text})

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500,
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    answer = response.json()["choices"][0]["message"]["content"]

    user_memory[user_id].append({"role": "user", "content": user_text})
    user_memory[user_id].append({"role": "assistant", "content": answer})

    return answer

# ================== КОМАНДЫ ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 AI Web3 & Crypto Assistant\n\n"
        "Я помогаю разбираться в:\n"
        "• Криптовалютах\n"
        "• Web3 и DeFi\n"
        "• AI-агентах и Fetch.ai\n"
        "• Реальных способах заработка\n\n"
        f"🆓 Бесплатно: {FREE_LIMIT} сообщений в день\n"
        "💎 Premium — без ограничений\n\n"
        "Задавай вопрос 👇"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Что я умею:\n\n"
        "• Объяснять крипту простыми словами\n"
        "• Помогать понять, как зарабатывать в Web3\n"
        "• Разбирать AI-агентов и Fetch.ai\n"
        "• Давать пошаговые инструкции\n\n"
        "Команды:\n"
        "/start — начало\n"
        "/premium — Premium доступ"
    )

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 Premium доступ\n\n"
        "Что даёт Premium:\n"
        "• Безлимитные запросы\n"
        "• Приоритетные ответы\n"
        "• Доступ к продвинутым темам\n\n"
        "Оплата скоро будет доступна.\n"
        "Следи за обновлениями 🚀"
    )

# ================== ОБРАБОТКА СООБЩЕНИЙ ==================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    today = date.today()

    # сброс лимита каждый день
    if user_usage[user_id]["date"] != today:
        user_usage[user_id] = {"date": today, "count": 0}

    # проверка лимита
    if user_id not in premium_users:
        if user_usage[user_id]["count"] >= FREE_LIMIT:
            await update.message.reply_text(
                "🚫 Лимит бесплатных сообщений исчерпан.\n\n"
                "💎 Оформи Premium, чтобы продолжить без ограничений.\n"
                "Команда: /premium"
            )
            return

        user_usage[user_id]["count"] += 1

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing",
    )

    answer = ask_groq(user_id, text)
    await update.message.reply_text(answer)

# ================== MAIN ==================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("premium", premium))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("✅ AI Web3 & Crypto Assistant с лимитами запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
