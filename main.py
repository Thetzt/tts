import os
import asyncio
import edge_tts
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder='.')

# Voice Mapping
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
        
        # UI မှ ဂဏန်းများကို ယူခြင်း
        raw_speed = float(request.form.get('speed', 1.0))
        raw_pitch = int(request.form.get('pitch', 0))
        raw_volume = int(request.form.get('volume', 100))
        
        # Native Parameter Conversion (SSML မသုံးတော့ပါ)
        # 1. Speed (Example: 1.15 -> +15%)
        speed_pct = f"{int((raw_speed - 1) * 100):+d}%"
        
        # 2. Pitch (Example: 5 -> +5Hz)
        pitch_str = f"{raw_pitch:+d}Hz"

        # 3. Volume (Example: 100 -> +0%, 50 -> -50%)
        vol_pct = f"{raw_volume - 100:+d}%"

        # 4. Voice ID
        voice_id = VOICES.get(voice_key, VOICES["male"])

        # Pause Handling: SSML မသုံးဘဲ ပုဒ်ဖြတ်ပုဒ်ရပ် ထည့်ခြင်း
        # စာကြောင်းကျော်ရင် ပုဒ်မ(။) ထည့်ပေးလိုက်ရင် AI က အလိုလို ခဏရပ်ပါမယ်
        final_text = text.replace('\n', ' ။ ')

        async def get_voice():
            # Native Arguments သုံးထားလို့ Code ဖတ်တဲ့ ပြဿနာ ကင်းရှင်းသွားပါပြီ
            communicate = edge_tts.Communicate(
                final_text, 
                voice_id, 
                rate=speed_pct, 
                pitch=pitch_str, 
                volume=vol_pct
            )
            await communicate.save(OUTPUT_FILE)
        
        asyncio.run(get_voice())
        return send_file(OUTPUT_FILE, as_attachment=False)

    except Exception as e:
        print(f"Error generating voice: {e}")
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)