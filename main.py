import os
import logging
import requests
from collections import defaultdict, deque

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

# храним последние 5 сообщений на пользователя
user_memory = defaultdict(lambda: deque(maxlen=5))

# ================== SYSTEM PROMPT ==================

SYSTEM_PROMPT = """
You are an AI Web3 & Crypto Assistant.

Your mission:
- Explain cryptocurrency, blockchain, Web3, AI agents, DeFi in simple language
- Help users understand real ways to earn in crypto and AI ecosystems
- Give structured, step-by-step answers
- Focus on practical tools, platforms, and strategies
- Avoid hype, scams, and vague advice

Rules:
- If a question is not related to crypto, Web3, AI, or earning online — politely redirect
- Do not give financial guarantees
- Be clear, confident, and professional
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

    try:
        response = requests.post(
            GROQ_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        # сохраняем контекст
        user_memory[user_id].append({"role": "user", "content": user_text})
        user_memory[user_id].append({"role": "assistant", "content": answer})

        return answer

    except Exception as e:
        logging.error(f"GROQ ERROR: {e}")
        return "⚠️ Ошибка AI. Попробуй позже."

# ================== COMMANDS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 AI Web3 & Crypto Assistant\n\n"
        "Я помогаю разбираться в:\n"
        "• Криптовалютах\n"
        "• Web3 и DeFi\n"
        "• AI-агентах и Fetch.ai\n"
        "• Реальных способах заработка\n\n"
        "Просто задай вопрос 👇"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Что я умею:\n\n"
        "• Объяснять крипту простыми словами\n"
        "• Помогать понять, как зарабатывать в Web3\n"
        "• Разбирать Fetch.ai и AI-агентов\n"
        "• Давать пошаговые инструкции\n\n"
        "Просто напиши вопрос."
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Обо мне\n\n"
        "Я AI-агент для Web3 и Crypto.\n"
        "Создан, чтобы экономить твоё время\n"
        "и давать понятные, практичные ответы."
    )

# ================== MESSAGE HANDLER ==================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing",
    )

    reply = ask_groq(user_id, user_text)
    await update.message.reply_text(reply)

# ================== MAIN ==================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("✅ AI Web3 & Crypto Assistant запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
