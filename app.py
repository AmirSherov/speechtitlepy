import tkinter as tk
import sounddevice as sd
import queue
import json
import threading
from vosk import Model, KaldiRecognizer

# === Настройки ===
SAMPLE_RATE = 16000
MODEL_PATH = "model"  # Папка с моделью

# === Загрузка модели ===
print("🔄 Загружаю модель Vosk...")
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)
q = queue.Queue()

# === Функция для обработки аудио ===
def audio_callback(indata, frames, time, status):
    q.put(bytes(indata))

def listen():
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):
        print("🎧 Слушаю... Говори!")
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                update_subtitle(text)

# === GUI (Tkinter) ===
root = tk.Tk()
root.title("🟡 Речевые субтитры (offline)")
root.geometry("800x200")
root.configure(bg="black")

label = tk.Label(root, text="🎤 Говорите...", font=("Helvetica", 24), fg="lime", bg="black", wraplength=760, justify="center")
label.pack(expand=True)

def update_subtitle(text):
    label.config(text=text)

# === Запуск в фоновом потоке ===
threading.Thread(target=listen, daemon=True).start()

# === Запуск окна ===
root.mainloop()
