import os
import asyncio
import edge_tts
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder='.')

# Default Voice (Thiha - Male)
VOICE = "my-MM-ThihaNeural"
OUTPUT_FILE = "voice.mp3"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    text = request.form.get('text')
    
    # UI မှ တန်ဖိုးများကို ယူခြင်း
    speed = request.form.get('speed', '+0%')
    volume = request.form.get('volume', '+0%')
    pitch = request.form.get('pitch', '+0Hz')
    
    # Console မှာ စစ်ကြည့်ရန် (Debug)
    print(f"Generating: {text[:20]}... | Speed: {speed} | Pitch: {pitch}")

    async def get_voice():
        communicate = edge_tts.Communicate(text, VOICE, rate=speed, volume=volume, pitch=pitch)
        await communicate.save(OUTPUT_FILE)
    
    try:
        asyncio.run(get_voice())
        return send_file(OUTPUT_FILE, as_attachment=False)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)