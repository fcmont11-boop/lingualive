from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import openai
import deepl
import subprocess
import base64
import tempfile
import os

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SECRET_KEY'] = 'translator123'
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='eventlet')

import os
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DEEPL_API_KEY = os.environ.get("DEEPL_API_KEY")

LANGUAGES = {
    "English": ("EN-US", "Samantha"),
    "Italian": ("IT", "Alice"),
    "Spanish": ("ES", "Eddy (Spanish (Spain))"),
    "French": ("FR", "Eddy (French (France))"),
    "German": ("DE", "Anna"),
    "Portuguese": ("PT-BR", "Eddy (Portuguese (Brazil))"),
}

rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    room = data['room']
    lang = data['language']
    join_room(room)
    if room not in rooms:
        rooms[room] = {}
    rooms[room][request.sid] = lang
    emit('status', {'msg': f'Joined room {room} as {lang} speaker'}, room=request.sid)
    emit('room_info', {'users': len(rooms[room])}, to=room)

@socketio.on('audio')
def on_audio(data):
    room = data['room']
    audio_b64 = data['audio']
    speaker_lang = data['language']
    audio_bytes = base64.b64decode(audio_b64)
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        with open(tmp_path, 'rb') as f:
            result = client.audio.transcriptions.create(model='whisper-1', file=f)
        text = result.text.strip()
        if not text:
            return
        target_lang = None
        for lang in rooms.get(room, {}).values():
            if lang != speaker_lang:
                target_lang = lang
                break
        if not target_lang:
            target_lang = "English"
        target_code, _ = LANGUAGES[target_lang]
        translator = deepl.Translator(DEEPL_API_KEY)
        translation = translator.translate_text(text, target_lang=target_code).text
        emit('transcript', {
            'speaker': speaker_lang,
            'original': text,
            'translation': translation,
            'target_lang': target_lang
        }, to=room)
    finally:
        os.unlink(tmp_path)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get("PORT", 5001)), debug=False)
