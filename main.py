import os
import logging
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# =========================================================
# ENV VARIABLES (Railway → Variables)
# =========================================================
# BOT_TOKEN        — Telegram bot token
# LLM_API_KEY     — API key (OpenAI / Groq / Together / OpenRouter)
# LLM_API_URL     — endpoint, например:
#                   https://api.openai.com/v1/chat/completions
#                   https://api.groq.com/openai/v1/chat/completions
#                   https://api.together.xyz/v1/chat/completions
# LLM_MODEL       — например: gpt-4o-mini, llama-3.1-70b, mixtral-8x7b

BOT_TOKEN = os.getenv("BOT_TOKEN")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_URL = os.getenv("LLM_API_URL")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан")
if not LLM_API_KEY or not LLM_API_URL:
    raise ValueError("LLM_API_KEY или LLM_API_URL не заданы")

# =========================================================
# SYSTEM PROMPT v2 (СТРОГИЙ)
# =========================================================
SYSTEM_PROMPT = """
Ты — AI-бот, созданный частным разработчиком (физическое лицо).
Страна оператора: Республика Казахстан.
Бот предоставляется бесплатно.

Ты используешь языковую модель LLaMA или совместимую LLM,
но не являешься официальным продуктом Meta Platforms, Inc.
и не аффилирован с Meta.

ГЛАВНОЕ ПРАВИЛО:
Лучше честно сказать «я не могу дать однозначный ответ»,
чем уверенно дать неправильный.

ОБЩИЕ ОГРАНИЧЕНИЯ:
- Не выдавай себя за Meta AI или официальный сервис Meta.
- Не называй себя экспертом или консультантом.
- Запрещено выдумывать факты, объекты, события.
- При нарушении условий задачи остановись и исправь ответ.

МЫШЛЕНИЕ (СКРЫТО):
- Перед ответом на логические и сложные вопросы
  сначала решай задачу ВНУТРЕННЕ.
- Ход рассуждений пользователю НЕ показывай.
- Показывай только итог и краткое объяснение.

КРИТИЧЕСКИЕ ПРАВИЛА ДЛЯ ЛОГИЧЕСКИХ ЗАДАЧ:
- Используй ТОЛЬКО сущности из условия.
- Не добавляй новые объекты или допущения.
- Строго соблюдай ограничения задачи.
- Не перебирай сценарии, если это запрещено.
- Если решение невозможно — скажи об этом прямо.

САМОПРОВЕРКА:
- Следует ли вывод строго из условий?
- Добавлены ли лишние сущности?
Если да — переформулируй ответ.

СТИЛЬ:
- Кратко (2–5 предложений).
- Без псевдонаучных слов.
- Без категоричности без строгого основания.
"""

# =========================================================
# LLM CALL (OpenAI-compatible)
# =========================================================
def call_llm(user_text: str) -> str:
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        "temperature": 0.2,
        "max_tokens": 500,
    }

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    r = requests.post(LLM_API_URL, json=payload, headers=headers, timeout=60)
    r.raise_for_status()

    data = r.json()
    return data["choices"][0]["message"]["content"].strip()

# =========================================================
# TELEGRAM HANDLERS
# =========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет 👋\n"
        "Я бесплатный AI-бот.\n"
        "Могу помогать с вопросами, но могу ошибаться.\n"
        "Используй ответы как подсказку, а не как истину."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        reply = call_llm(user_text)
    except Exception as e:
        logging.exception(e)
        reply = "Произошла ошибка. Попробуй позже."

    await update.message.reply_text(reply)

# =========================================================
# MAIN
# =========================================================
def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
