import os
import asyncio
import edge_tts
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder='.')

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
    try:
        text = request.form.get('text')
        voice_key = request.form.get('voice', 'male')
        file_format = request.form.get('format', 'mp3') # UI မှ Format ကို လှမ်းယူမည်
        
        # Parameters
        raw_speed = float(request.form.get('speed', 1.0))
        raw_pitch = int(request.form.get('pitch', 0))
        raw_volume = int(request.form.get('volume', 100))
        
        # Conversions
        speed_pct = f"{int((raw_speed - 1) * 100):+d}%"
        pitch_str = f"{raw_pitch:+d}Hz"
        vol_pct = f"{raw_volume - 100:+d}%"
        voice_id = VOICES.get(voice_key, VOICES["male"])

        # Pause Handling
        final_text = text.replace('\n', ' ။ ')

        async def get_voice():
            communicate = edge_tts.Communicate(
                final_text, 
                voice_id, 
                rate=speed_pct, 
                pitch=pitch_str, 
                volume=vol_pct
            )
            await communicate.save(OUTPUT_FILE)
        
        asyncio.run(get_voice())

        # Browser ကို ဇဝေဇဝါမဖြစ်အောင် MimeType ပြောင်းပေးခြင်း
        # WAV ရွေးရင် WAV header နဲ့ပို့မယ် (ဒါမှ .mp3 ထပ်မတိုးမှာ)
        mime_type = 'audio/wav' if file_format == 'wav' else 'audio/mpeg'

        return send_file(OUTPUT_FILE, mimetype=mime_type, as_attachment=False)

    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)