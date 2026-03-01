import os
import whisper
import asyncio
from groq import Groq
import edge_tts

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================= НАСТРОЙКИ =================
TELEGRAM_TOKEN = "PASTE_TELEGRAM_BOT_TOKEN"
GROQ_API_KEY = "PASTE_GROQ_API_KEY"

VOICE_INPUT = "voice.ogg"
VOICE_OUTPUT = "answer.mp3"
# ============================================

# Whisper
whisper_model = whisper.load_model("base")

# Groq
groq_client = Groq(api_key=GROQ_API_KEY)


def ask_groq(text: str) -> str:
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты голосовой AI-ассистент. "
                    "Отвечай кратко, понятно и по делу."
                ),
            },
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content


async def text_to_speech(text: str):
    tts = edge_tts.Communicate(
        text=text,
        voice="ru-RU-DmitryNeural",
    )
    await tts.save(VOICE_OUTPUT)


# ================= HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎙 Отправь голосовое сообщение — я отвечу голосом."
    )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎧 Слушаю...")

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    # 1️⃣ скачать аудио
    await file.download_to_drive(VOICE_INPUT)

    # 2️⃣ Whisper → текст
    result = whisper_model.transcribe(VOICE_INPUT, language="ru")
    user_text = result.get("text", "").strip()

    if not user_text:
        await update.message.reply_text("❌ Не смог распознать голос.")
        return

    # 3️⃣ Groq → ответ
    answer_text = ask_groq(user_text)

    # 4️⃣ TTS → голос
    await text_to_speech(answer_text)

    # 5️⃣ отправить голос
    with open(VOICE_OUTPUT, "rb") as audio:
        await update.message.reply_voice(audio)

    # 6️⃣ очистка
    os.remove(VOICE_INPUT)
    os.remove(VOICE_OUTPUT)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎙 Пожалуйста, отправь ГОЛОСОВОЕ сообщение."
    )

# ============================================


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()
