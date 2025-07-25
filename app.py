import tkinter as tk
import speech_recognition as sr
import threading
import pyaudio

class SubtitleApp:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        
        # Создание GUI
        self.root = tk.Tk()
        self.root.title("🎧 Субтитры из динамиков")
        self.root.geometry("900x300")
        self.root.configure(bg="black")
        
        # Основной текст субтитров
        self.label = tk.Label(
            self.root, 
            text="🎶 Готов к прослушиванию...", 
            font=("Helvetica", 20), 
            fg="lime", 
            bg="black", 
            wraplength=860, 
            justify="center"
        )
        self.label.pack(expand=True, pady=20)
        
        # Статус
        self.status_label = tk.Label(
            self.root, 
            text="Выберите устройство для начала", 
            font=("Helvetica", 12), 
            fg="yellow", 
            bg="black"
        )
        self.status_label.pack(side=tk.BOTTOM, pady=10)
        
        # Кнопки управления
        self.button_frame = tk.Frame(self.root, bg="black")
        self.button_frame.pack(side=tk.BOTTOM, pady=10)
        
        self.start_button = tk.Button(
            self.button_frame, 
            text="▶️ Начать", 
            command=self.start_listening,
            bg="green", 
            fg="white", 
            font=("Helvetica", 12)
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(
            self.button_frame, 
            text="⏹️ Остановить", 
            command=self.stop_listening,
            bg="red", 
            fg="white", 
            font=("Helvetica", 12),
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.devices_button = tk.Button(
            self.button_frame, 
            text="🎤 Устройства", 
            command=self.show_devices,
            bg="blue", 
            fg="white", 
            font=("Helvetica", 12)
        )
        self.devices_button.pack(side=tk.LEFT, padx=5)
        
        # Переменная для хранения выбранного устройства
        self.device_index = None
        
    def get_audio_devices(self):
        """Получить список всех аудио устройств"""
        p = pyaudio.PyAudio()
        devices = []
        
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            # Ищем устройства ввода (микрофоны, стерео микс)
            if info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxInputChannels']
                })
        
        p.terminate()
        return devices
    
    def show_devices(self):
        """Показать окно выбора устройства"""
        devices_window = tk.Toplevel(self.root)
        devices_window.title("Выбор аудио устройства")
        devices_window.geometry("600x400")
        devices_window.configure(bg="gray20")
        
        tk.Label(
            devices_window, 
            text="Выберите устройство ввода (Стерео микс / Stereo Mix):",
            font=("Helvetica", 14),
            fg="white",
            bg="gray20"
        ).pack(pady=10)
        
        # Список устройств
        listbox = tk.Listbox(
            devices_window,
            font=("Courier", 10),
            bg="gray10",
            fg="white",
            selectbackground="blue"
        )
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        devices = self.get_audio_devices()
        for device in devices:
            listbox.insert(tk.END, f"[{device['index']}] {device['name']} (каналы: {device['channels']})")
        
        def select_device():
            selection = listbox.curselection()
            if selection:
                self.device_index = devices[selection[0]]['index']
                device_name = devices[selection[0]]['name']
                self.status_label.config(text=f"Выбрано: {device_name}")
                devices_window.destroy()
        
        tk.Button(
            devices_window,
            text="Выбрать",
            command=select_device,
            bg="green",
            fg="white",
            font=("Helvetica", 12)
        ).pack(pady=10)
        
        # Инструкция
        instruction = tk.Text(
            devices_window,
            height=6,
            font=("Helvetica", 9),
            bg="gray30",
            fg="white",
            wrap=tk.WORD
        )
        instruction.pack(fill=tk.X, padx=20, pady=10)
        instruction.insert(tk.END, 
            "ВАЖНО: Для захвата системного звука нужно включить 'Стерео микс':\n"
            "1. Щелкните правой кнопкой по значку звука в трее\n"
            "2. Выберите 'Звуки' → 'Запись'\n"
            "3. Щелкните правой кнопкой → 'Показать отключенные устройства'\n"
            "4. Включите 'Стерео микс' и установите как устройство по умолчанию\n"
            "5. Выберите его в списке выше"
        )
        instruction.config(state=tk.DISABLED)
    
    def start_listening(self):
        """Начать прослушивание"""
        if self.device_index is None:
            self.status_label.config(text="❌ Сначала выберите устройство!")
            return
            
        self.is_listening = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.label.config(text="🎧 Слушаю системный звук...")
        
        # Запуск в отдельном потоке
        self.listen_thread = threading.Thread(target=self.recognize_loop, daemon=True)
        self.listen_thread.start()
    
    def stop_listening(self):
        """Остановить прослушивание"""
        self.is_listening = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.label.config(text="⏹️ Прослушивание остановлено")
    
    def recognize_loop(self):
        """Основной цикл распознавания"""
        try:
            mic = sr.Microphone(device_index=self.device_index)
            
            with mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.status_label.config(text="✅ Слушаю...")
                
                while self.is_listening:
                    try:
                        # Слушаем с таймаутом
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                        
                        # Распознаем речь
                        text = self.recognizer.recognize_google(audio, language="ru-RU")
                        print(f"🗣️ {text}")
                        
                        # Обновляем UI в главном потоке
                        self.root.after(0, lambda: self.label.config(text=text))
                        
                    except sr.WaitTimeoutError:
                        # Таймаут - это нормально, продолжаем слушать
                        pass
                    except sr.UnknownValueError:
                        # Не удалось распознать
                        self.root.after(0, lambda: self.label.config(text="😶 Не понял..."))
                    except sr.RequestError as e:
                        # Ошибка API
                        self.root.after(0, lambda: self.label.config(text=f"❌ Ошибка API: {e}"))
                        break
                        
        except OSError as e:
            self.root.after(0, lambda: self.status_label.config(text=f"❌ Ошибка устройства: {e}"))
            self.root.after(0, self.stop_listening)
    
    def run(self):
        """Запустить приложение"""
        self.root.mainloop()

# Запуск приложения
if __name__ == "__main__":
    app = SubtitleApp()
    app.run()