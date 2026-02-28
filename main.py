import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# =========================================================
# ENV
# =========================================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_URL = os.getenv("LLM_API_URL")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")

if not all([BOT_TOKEN, LLM_API_KEY, LLM_API_URL]):
    raise RuntimeError("ENV variables not set")

# =========================================================
# SYSTEM PROMPT — HARD CONTROL
# =========================================================
SYSTEM_PROMPT = """
Ты — AI-бот, созданный частным разработчиком (физическое лицо).
Страна оператора: Республика Казахстан.
Бот бесплатный.

Ты используешь LLM (включая LLaMA), но не являешься продуктом Meta
и не аффилирован с Meta Platforms, Inc.

────────────────────────────────
ГЛАВНОЕ ПРАВИЛО
────────────────────────────────
Лучше ответить «невозможно определить», чем дать неверный ответ.

────────────────────────────────
СТРОГИЕ ЗАПРЕТЫ
────────────────────────────────
- Запрещено описывать ход рассуждений.
- Запрещено предлагать альтернативные шаги.
- Запрещено использовать слова:
  «давайте», «попробуем», «если», «возможно», «шанс».
- Запрещено добавлять сущности вне условия.
- Запрещено нарушать ограничения задачи.

────────────────────────────────
ЛОГИЧЕСКИЕ ЗАДАЧИ (КРИТИЧНО)
────────────────────────────────
1. Решай задачу ВНУТРЕННЕ.
2. Пользователю показывай ТОЛЬКО финальный вывод.
3. Ответ — не более 4 предложений.
4. Если решение не следует строго из условий —
   напиши: «Однозначный ответ определить невозможно».

────────────────────────────────
ФОРМАТ ОТВЕТА
────────────────────────────────
- Кратко
- По существу
- Без уверенности без основания
"""

# =========================================================
# LLM CALL
# =========================================================
def call_llm(user_text: str) -> str:
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        "temperature": 0.1,
        "max_tokens": 200,
    }

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    r = requests.post(LLM_API_URL, json=payload, headers=headers, timeout=40)
    r.raise_for_status()

    text = r.json()["choices"][0]["message"]["content"].strip()

    # === FINAL SAFETY FILTER ===
    banned = ["давайте", "попробуем", "шанс", "возможно", "если"]
    if any(word in text.lower() for word in banned):
        return "Однозначный ответ определить невозможно."

    if len(text.split(".")) > 5:
        return "Однозначный ответ определить невозможно."

    return text

# =========================================================
# TELEGRAM
# =========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет 👋\n"
        "Я бесплатный AI-бот.\n"
        "Могу ошибаться. Используй ответы как подсказку."
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        reply = call_llm(update.message.text)
    except Exception as e:
        logging.exception(e)
        reply = "Ошибка. Попробуй позже."
    await update.message.reply_text(reply)

# =========================================================
# MAIN
# =========================================================
def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("🤖 BOT RUNNING")
    app.run_polling()

if __name__ == "__main__":
    main()
