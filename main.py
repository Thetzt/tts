import os
import asyncio
import edge_tts
from flask import Flask, request, send_file, render_template

# Template တွေကို လက်ရှိ Folder ထဲမှာပဲ ရှာခိုင်းတာပါ
app = Flask(__name__, template_folder='.')

VOICE = "my-MM-ThihaNeural"
OUTPUT_FILE = "voice.mp3"

# ပင်မစာမျက်နှာ (index.html) ကို ပြပေးမယ့်နေရာ
@app.route('/')
def home():
    return render_template('index.html')

# Generate ခလုတ်နှိပ်လိုက်ရင် အလုပ်လုပ်မယ့်နေရာ
@app.route('/generate', methods=['POST'])
def generate():
    text = request.form['text']
    
    # Python Code နဲ့ အသံဖိုင်ထုတ်ခြင်း
    async def get_voice():
        communicate = edge_tts.Communicate(text, VOICE, rate="+10%")
        await communicate.save(OUTPUT_FILE)
    
    asyncio.run(get_voice())
    
    # ရလာတဲ့ အသံဖိုင်ကို ပြန်ပို့ပေးခြင်း
    return send_file(OUTPUT_FILE, as_attachment=False)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
