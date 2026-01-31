import os
import asyncio
import edge_tts
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

# --- 1. Edge TTS အပိုင်း ---
VOICE = "my-MM-ThihaNeural"
OUTPUT_FILE = "voice.mp3"

async def generate_voice(text):
    communicate = edge_tts.Communicate(text, VOICE, rate="+10%")
    await communicate.save(OUTPUT_FILE)
    return OUTPUT_FILE

# --- 2. Telegram Bot အပိုင်း ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Mingalarbar! စာပို့လိုက်ရင် အသံဖိုင် ပြောင်းပေးပါမယ်။")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text("အသံဖိုင် လုပ်နေပါပြီ... ခဏစောင့်ပါ...")
    
    try:
        # TTS ထုတ်ခြင်း
        audio_path = await generate_voice(user_text)
        # အသံဖိုင်ပြန်ပို့ခြင်း
        await update.message.reply_audio(audio=open(audio_path, 'rb'))
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# --- 3. Web Server (Render မပိတ်အောင် ထိန်းထားရန်) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- 4. Main Function ---
if __name__ == "__main__":
    # Flask ကို Thread တစ်ခုနဲ့ Run
    threading.Thread(target=run_flask).start()
    
    # Telegram Bot ကို Run
    # TOKEN ကို Render Environment Variable မှာ ထည့်ရမယ်
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN မရှိပါ။")
    else:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("Bot စတင်နေပါပြီ...")
        application.run_polling()
