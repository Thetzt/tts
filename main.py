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
        
        # UI မှ တန်ဖိုးများကို ရယူခြင်း
        raw_speed = float(request.form.get('speed', 1.0))
        raw_pitch = request.form.get('pitch', '+0Hz')
        raw_volume = int(request.form.get('volume', 100))
        pause_ms = request.form.get('pause', '300') # Default 300 from backend fallback

        # 1. Speed Calculation (e.g. 1.0 -> +0%, 1.2 -> +20%)
        speed_pct = f"{int((raw_speed - 1) * 100):+d}%"
        
        # 2. Volume Calculation (e.g. 100 -> +0%)
        vol_pct = f"{raw_volume - 100:+d}%"

        # 3. Pause Handling (SSML break)
        break_tag = f' <break time="{pause_ms}ms"/> '
        formatted_text = text.replace('\n', break_tag)

        # 4. Construct SSML
        voice_id = VOICES.get(voice_key, VOICES["male"])
        
        ssml_text = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='my-MM'>
            <voice name='{voice_id}'>
                <prosody rate='{speed_pct}' pitch='{raw_pitch}' volume='{vol_pct}'>
                    {formatted_text}
                </prosody>
            </voice>
        </speak>
        """

        async def get_voice():
            communicate = edge_tts.Communicate(ssml_text, voice_id)
            await communicate.save(OUTPUT_FILE)
        
        asyncio.run(get_voice())
        return send_file(OUTPUT_FILE, as_attachment=False)

    except Exception as e:
        # Error တက်ရင် ဘာကြောင့်လဲ သိရအောင် log ထုတ်ပေးမယ်
        print(f"Error generating voice: {e}")
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)