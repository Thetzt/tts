import os
import asyncio
import edge_tts
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, send_file # send_file ကို အသစ်ထပ်ထည့်ထားသည်
import threading

# --- 1. Edge TTS Config ---
VOICE = "my-MM-ThihaNeural"
OUTPUT_FILE = "voice.mp3"

async def generate_voice(text):
    communicate = edge_tts.Communicate(text, VOICE, rate="+15%") # Recap အတွက် +15%
    await communicate.save(OUTPUT_FILE)
    return OUTPUT_FILE

# --- 2. Telegram Bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ! Recap စာသားကို ပို့လိုက်ရင် အသံဖိုင် လုပ်ပေးပါမယ်။")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    status_msg = await update.message.reply_text("အသံဖိုင် လုပ်နေပါပြီ... ⏳")
    
    try:
        audio_path = await generate_voice(user_text)
        await update.message.reply_audio(audio=open(audio_path, 'rb'), title="Recap Voice")
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=status_msg.message_id)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# --- 3. Web Server (Updated for HTML) ---
app = Flask(__name__)

@app.route('/')
def home():
    # index.html ကို ပြပေးမည့် အပိုင်း
    try:
        return send_file('index.html')
    except Exception as e:
        return "Bot is running! (index.html not found)"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- 4. Main Execution ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN မရှိပါ။")
    else:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("Bot စတင်နေပါပြီ...")
        application.run_polling()
