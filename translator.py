import sounddevice as sd
import scipy.io.wavfile as wav
import openai
import deepl
import subprocess
import threading
import tkinter as tk
from tkinter import scrolledtext

OPENAI_API_KEY = "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"
DEEPL_API_KEY = "9d136d63-7466-4668-88f3-27b11f2f5df7:fx"

SAMPLE_RATE = 44100
DURATION = 5

LANGUAGES = {
    "English": ("EN-US", "Samantha"),
    "Italian": ("IT", "Alice"),
    "Spanish": ("ES", "Eddy (Spanish (Spain))"),
    "French": ("FR", "Eddy (French (France))"),
    "German": ("DE", "Anna"),
    "Portuguese": ("PT-BR", "Eddy (Portuguese (Brazil))"),
}

def record_audio():
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()
    wav.write("input.wav", SAMPLE_RATE, recording)

def transcribe_audio():
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    with open("input.wav", "rb") as f:
        result = client.audio.transcriptions.create(model="whisper-1", file=f)
    return result.text

def translate_text(text, target_code):
    translator = deepl.Translator(DEEPL_API_KEY)
    result = translator.translate_text(text, target_lang=target_code)
    return result.text

def speak_text(text, voice):
    subprocess.run(["say", "-v", voice, text])

def log(widget, message):
    widget.configure(state="normal")
    widget.insert(tk.END, message + "\n")
    widget.see(tk.END)
    widget.configure(state="disabled")

def handle_speaker(speaker_lang, target_lang, transcript):
    target_code, target_voice = LANGUAGES[target_lang]
    log(transcript, f"Recording {speaker_lang}... Speak now!")
    record_audio()
    text = transcribe_audio()
    if text.strip() == "":
        log(transcript, "Nothing heard, try again.")
        return
    log(transcript, f"{speaker_lang}: {text}")
    translation = translate_text(text, target_code)
    log(transcript, f"{target_lang}: {translation}")
    speak_text(translation, target_voice)
    log(transcript, "---")

def press_a(lang_a_var, lang_b_var, transcript, btn_a, btn_b):
    btn_a.configure(state="disabled")
    btn_b.configure(state="disabled")
    t = threading.Thread(target=lambda: [
        handle_speaker(lang_a_var.get(), lang_b_var.get(), transcript),
        btn_a.configure(state="normal"),
        btn_b.configure(state="normal")
    ])
    t.daemon = True
    t.start()

def press_b(lang_a_var, lang_b_var, transcript, btn_a, btn_b):
    btn_a.configure(state="disabled")
    btn_b.configure(state="disabled")
    t = threading.Thread(target=lambda: [
        handle_speaker(lang_b_var.get(), lang_a_var.get(), transcript),
        btn_a.configure(state="normal"),
        btn_b.configure(state="normal")
    ])
    t.daemon = True
    t.start()

root = tk.Tk()
root.title("Voice Translator")
root.geometry("620x550")
root.configure(bg="#2c3e50")

tk.Label(root, text="Voice Translator", font=("Helvetica", 24, "bold"), bg="#2c3e50", fg="white").pack(pady=15)

frame = tk.Frame(root, bg="#2c3e50")
frame.pack(pady=5)

tk.Label(frame, text="Person A:", bg="#2c3e50", fg="white", font=("Helvetica", 12)).grid(row=0, column=0, padx=10)
lang_a_var = tk.StringVar(value="English")
tk.OptionMenu(frame, lang_a_var, *LANGUAGES.keys()).grid(row=0, column=1, padx=10)

tk.Label(frame, text="Person B:", bg="#2c3e50", fg="white", font=("Helvetica", 12)).grid(row=0, column=2, padx=10)
lang_b_var = tk.StringVar(value="Italian")
tk.OptionMenu(frame, lang_b_var, *LANGUAGES.keys()).grid(row=0, column=3, padx=10)

transcript = scrolledtext.ScrolledText(root, width=70, height=15, state="disabled", bg="#34495e", fg="white", font=("Helvetica", 11))
transcript.pack(pady=15, padx=20)

btn_frame = tk.Frame(root, bg="#2c3e50")
btn_frame.pack(pady=10)

btn_a = tk.Button(btn_frame, text="Person A - Speak", font=("Helvetica", 13, "bold"), bg="#3498db", fg="white", padx=20, pady=10)
btn_b = tk.Button(btn_frame, text="Person B - Speak", font=("Helvetica", 13, "bold"), bg="#9b59b6", fg="white", padx=20, pady=10)

btn_a.configure(command=lambda: press_a(lang_a_var, lang_b_var, transcript, btn_a, btn_b))
btn_b.configure(command=lambda: press_b(lang_a_var, lang_b_var, transcript, btn_a, btn_b))

btn_a.grid(row=0, column=0, padx=20)
btn_b.grid(row=0, column=1, padx=20)

root.mainloop()
