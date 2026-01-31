import os
import asyncio
import edge_tts
from flask import Flask, request, send_file, render_template

app = Flask(__name__, template_folder='.')

# Voice Mapping (UI မှာ Male/Female ပဲပြပြီး Backend မှာ နာမည်နဲ့ချိတ်ပါမယ်)
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
        
        # UI က ပို့လိုက်တဲ့ ဂဏန်းတွေကို SSML တန်ဖိုးပြောင်းခြင်း
        raw_speed = float(request.form.get('speed', 1.0))
        raw_pitch = request.form.get('pitch', '0Hz')
        raw_volume = int(request.form.get('volume', 100))
        pause_ms = request.form.get('pause', '0')

        # 1. Speed Calculation (Example: 1.5 -> +50%)
        speed_pct = f"{int((raw_speed - 1) * 100):+d}%"
        
        # 2. Volume Calculation (Example: 100 -> +0%, 50 -> -50%)
        # edge-tts volume works best with percentages relative to default
        vol_pct = f"{raw_volume - 100:+d}%"

        # 3. Pause Handling (Replace newlines with break tags)
        # စာကြောင်းအသစ်ဆင်းတိုင်း pause ထည့်ပါမယ်
        break_tag = f' <break time="{pause_ms}ms"/> '
        formatted_text = text.replace('\n', break_tag)

        # 4. Construct SSML (အသံ၊ အမြန်နှုန်း၊ အနိမ့်အမြင့် ပေါင်းစပ်ခြင်း)
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
            # SSML သုံးတဲ့အတွက် Communicate မှာ text နေရာ ssml ထည့်ရပါတယ်
            communicate = edge_tts.Communicate(ssml_text, voice_id)
            await communicate.save(OUTPUT_FILE)
        
        asyncio.run(get_voice())
        return send_file(OUTPUT_FILE, as_attachment=False)

    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)