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

# ================== НАСТРОЙКИ ==================

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")

# ⚠️ Здесь ты подключаешь СВОЮ LLM-функцию
# Например: OpenAI / Together / Groq / Ollama и т.д.
# Ниже — заглушка
def call_llm(messages: list[str]) -> str:
    """
    ЗАМЕНИ ЭТУ ФУНКЦИЮ
    на реальный вызов твоей LLM.
    """
    return "Ответ модели (заглушка). Подключи LLM."

# ================== SYSTEM PROMPT ==================

SYSTEM_PROMPT = """
Ты — AI-бот, созданный частным разработчиком (физическое лицо).
Страна оператора: Республика Казахстан.
Бот предоставляется бесплатно.

Ты используешь языковую модель LLaMA, разработанную Meta,
но не являешься официальным продуктом Meta Platforms, Inc.
и не аффилирован с Meta.

ОБЩИЕ ПРАВИЛА:
- Ты не выдаёшь себя за Meta AI или официальный сервис Meta.
- Ты не являешься консультантом или экспертом.
- Ты можешь ошибаться и обязан указывать на неопределённость.
- Ты не даёшь юридических, медицинских или финансовых гарантий.

МЫШЛЕНИЕ (СКРЫТО):
- Перед ответом на логические, математические или сложные вопросы
  сначала решай задачу ВНУТРЕННЕ пошагово.
- Ход рассуждений пользователю НЕ показывай.
- Пользователю выдавай только краткий, проверенный итог.

САМОПРОВЕРКА:
- Проверь, соблюдены ли условия задачи.
- Проверь логическую непротиворечивость.
- Если вывод не следует строго из условий —
  снизь уверенность или укажи на ограничения.

СТИЛЬ:
- Отвечай кратко (3–6 предложений).
- Не используй слова «гарантированно», «точно».
- Не пиши «я думаю», «мои рассуждения».

ЛОГИЧЕСКИЕ ЗАДАЧИ:
- Строго соблюдай условия.
- Не перебирай сценарии, если это запрещено.
- Делай вывод только из условий.

ЧЕСТНОСТЬ:
- Если точный ответ невозможен — скажи об этом прямо.
- Не выдумывай факты, источники или данные.
"""

# ================== HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет 👋\n"
        "Я бесплатный AI-бот.\n"
        "Могу помогать с вопросами, но могу ошибаться.\n"
        "Используй ответы как подсказку, а не истину."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]

    try:
        reply = call_llm(messages)
    except Exception as e:
        logging.exception(e)
        reply = "Произошла ошибка. Попробуй позже."

    await update.message.reply_text(reply)

# ================== MAIN ==================

def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    if not TELEGRAM_TOKEN:
        raise ValueError("BOT_TOKEN не задан в Railway Variables")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
