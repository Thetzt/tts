import os
import asyncio
import edge_tts
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder='.')

# အသံများ သတ်မှတ်ခြင်း
VOICES = {
    "male": "my-MM-ThihaNeural",
    "female": "my-MM-ThiriNeural"
}

OUTPUT_FILE = "voice.mp3"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    text = request.form.get('text')
    voice_key = request.form.get('voice', 'male') # Default male
    speed = request.form.get('speed', '+0%')
    pitch = request.form.get('pitch', '+0Hz')
    volume = request.form.get('volume', '+0%')
    
    # Select Voice ID
    selected_voice = VOICES.get(voice_key, VOICES["male"])

    async def get_voice():
        communicate = edge_tts.Communicate(text, selected_voice, rate=speed, pitch=pitch, volume=volume)
        await communicate.save(OUTPUT_FILE)
    
    try:
        asyncio.run(get_voice())
        return send_file(OUTPUT_FILE, as_attachment=False)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)