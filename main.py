import os
import uuid
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from gtts import gTTS

# =========================
# ENV
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в переменных окружения")

# =========================
# FastAPI
# =========================
app = FastAPI()

# =========================
# Telegram Application
# =========================
telegram_app: Application = ApplicationBuilder().token(BOT_TOKEN).build()

# =========================
# TTS (Text -> Voice)
# =========================
def text_to_voice(text: str, lang: str = "ru") -> str:
    filename = f"voice_{uuid.uuid4().hex}.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    return filename

# =========================
# Message handler
# =========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_text = update.message.text

    # 🔹 ЛОГИКА ОТВЕТА (можешь заменить на свою)
    reply_text = f"Вы написали: {user_text}"

    # 🔊 Озвучка
    voice_file = text_to_voice(reply_text)

    # 📤 Отправка voice
    with open(voice_file, "rb") as audio:
        await context.bot.send_voice(chat_id=chat_id, voice=audio)

    # 🧹 Очистка
    os.remove(voice_file)

# =========================
# Register handler
# =========================
telegram_app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
)

# =========================
# Webhook endpoint (Railway)
# =========================
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

# =========================
# Root (health check)
# =========================
@app.get("/")
async def root():
    return {"status": "ok"}
