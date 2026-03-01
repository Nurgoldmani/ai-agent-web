import os
import asyncio
import whisper
from aiogram import Bot, Dispatcher, executor, types
from groq import Groq
import edge_tts

# ================== НАСТРОЙКИ ==================
TELEGRAM_TOKEN = "PASTE_TELEGRAM_TOKEN"
GROQ_API_KEY = "PASTE_GROQ_API_KEY"

VOICE_INPUT = "voice.ogg"
VOICE_OUTPUT = "answer.mp3"

# ===============================================

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Whisper модель
whisper_model = whisper.load_model("base")

# Groq клиент
groq_client = Groq(api_key=GROQ_API_KEY)


def ask_groq(text: str) -> str:
    chat = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Ты полезный голосовой AI-ассистент. Отвечай кратко и понятно."},
            {"role": "user", "content": text}
        ],
    )
    return chat.choices[0].message.content


async def speak(text: str):
    communicate = edge_tts.Communicate(
        text=text,
        voice="ru-RU-DmitryNeural"
    )
    await communicate.save(VOICE_OUTPUT)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "🎙 Отправь мне голосовое сообщение — я отвечу голосом."
    )


@dp.message_handler(content_types=types.ContentType.VOICE)
async def handle_voice(message: types.Message):
    await message.answer("⏳ Слушаю тебя...")

    # 1️⃣ Скачать голос
    file = await bot.get_file(message.voice.file_id)
    await bot.download_file(file.file_path, VOICE_INPUT)

    # 2️⃣ Whisper → текст
    result = whisper_model.transcribe(VOICE_INPUT, language="ru")
    user_text = result["text"]

    if not user_text.strip():
        await message.answer("❌ Не смог распознать речь")
        return

    # 3️⃣ Groq → ответ
    answer_text = ask_groq(user_text)

    # 4️⃣ TTS → голос
    await speak(answer_text)

    # 5️⃣ Отправить голос
    with open(VOICE_OUTPUT, "rb") as audio:
        await message.answer_voice(audio)

    # 6️⃣ Очистка
    os.remove(VOICE_INPUT)
    os.remove(VOICE_OUTPUT)


if __name__ == "__main__":
    print("🤖 Бот запущен")
    executor.start_polling(dp, skip_updates=True)
