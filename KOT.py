# █▀▀█  █   █ 　  █▀▀█  █▀▀█ ▀▀█▀▀ 　  █▀▀▄  █▀▀▀  █   █ 　  █▀▀█  █▀▀▀█  █▀▀▄  █▀▀▀ 　 ▄ ▀▄ 
# █▀▀▄  █▄▄▄█ 　  █     █▄▄█   █   　  █  █  █▀▀▀   █ █  　  █     █   █  █  █  █▀▀▀ 　    █ 
# █▄▄█    █   　  █▄▄█  █  █   █   　  █▄▄▀  █▄▄▄   ▀▄▀  　  █▄▄█  █▄▄▄█  █▄▄▀  █▄▄▄ 　 ▀ ▄▀

import os
import pyaudio
import json
import threading
import webbrowser
from datetime import datetime
from vosk import Model, KaldiRecognizer
import pygame
import logging
import tkinter as tk
from PIL import Image, ImageTk
import pyautogui as pg
from pynput.keyboard import Controller, Key
import time

keyboard = Controller()

MODEL_PATH = "vosk"
COMMANDS_FILE = 'custom_commands.json'
LOG_FILE = 'log.txt'
POSITION_FILE = r'KotFiles\cat_position.txt'

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

pygame.mixer.init()

success_sound = pygame.mixer.Sound("success.mp3")
failure_sound = pygame.mixer.Sound("failure.mp3")

class CatWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("Кот")
        self.root.overrideredirect(True)

        self.cat_image = ImageTk.PhotoImage(Image.open("holiday_cat_image.png"))
        self.cat_open_image = ImageTk.PhotoImage(Image.open("cat_open.png"))

        self.label = tk.Label(root, image=self.cat_image)
        self.label.pack()

        self.is_dragging = False
        self.start_x = 0
        self.start_y = 0

        self.label.bind("<ButtonPress-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.do_drag)
        self.label.bind("<ButtonRelease-1>", self.stop_drag)

        self.load_position()

    def start_drag(self, event):
        self.is_dragging = True
        self.start_x = event.x
        self.start_y = event.y

    def do_drag(self, event):
        if self.is_dragging:
            x = self.root.winfo_x() - self.start_x + event.x
            y = self.root.winfo_y() - self.start_y + event.y
            self.root.geometry(f"+{x}+{y}")

    def stop_drag(self, event):
        self.is_dragging = False
        self.save_position()

    def open_mouth(self):
        self.label.config(image=self.cat_open_image)
        self.root.after(1000, self.close_mouth)

    def close_mouth(self):
        self.label.config(image=self.cat_image)

    def load_position(self):
        try:
            with open(POSITION_FILE, 'r') as f:
                position = f.read().strip().split(',')
                if len(position) == 2:
                    x, y = map(int, position)
                    self.root.geometry(f"+{x}+{y}")
                    logging.info(f"Позиция кота загружена: ({x}, {y})")
        except FileNotFoundError:
            logging.warning("Файл с позицией не найден. Используется стандартное положение.")
        except Exception as e:
            logging.error(f"Ошибка при загрузке позиции: {e}")

    def save_position(self):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        with open(POSITION_FILE, 'w') as f:
            f.write(f"{x},{y}")
            logging.info(f"Позиция кота сохранена: ({x}, {y})")

class VoiceAssistant:
    def __init__(self):
        self.model = self.load_model()
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.mic = pyaudio.PyAudio()
        self.stream = self.open_microphone()
        self.running = True
        self.custom_commands = self.load_custom_commands()
        self.cat_widget = CatWidget(tk.Tk())

    def load_model(self):
        try:
            model = Model(MODEL_PATH)
            logging.info("Модель загружена успешно.")
            return model
        except Exception as e:
            logging.error(f"Ошибка при загрузке модели: {e}")
            exit(1)

    def open_microphone(self):
        try:
            stream = self.mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
            stream.start_stream()
            logging.info("Микрофон открыт успешно.")
            return stream
        except Exception as e:
            logging.error(f"Ошибка при открытии микрофона: {e}")
            exit(1)

    def load_custom_commands(self):
        if os.path.exists(COMMANDS_FILE):
            with open(COMMANDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_custom_commands(self):
        with open(COMMANDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.custom_commands, f, ensure_ascii=False, indent=4)

    def add_custom_command(self, command, actions):
        self.custom_commands[command] = actions
        self.save_custom_commands()
        logging.info(f"Добавлена новая команда: {command} -> {actions}")

    def recognize_speech_from_mic(self):
        logging.info("Ассистент готов к распознаванию речи.")
        print("Скажите команду...")
        while self.running:
            try:
                data = self.stream.read(4000, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    if 'text' in result:
                        spoken_text = result['text'].strip()
                        if spoken_text:
                            logging.info(f"Вы сказали: {spoken_text}")
                            print(f"Вы сказали: {spoken_text}")
                            self.process_command(spoken_text)
            except Exception as e:
                logging.error(f"Ошибка при распознавании речи: {e}")

    def process_command(self, spoken_text):
        activators = ["кот ", "котик ", "котяра ", "киса ", "код ", "коды "]
        if any(activator in spoken_text for activator in activators):
            for activator in activators:
                spoken_text = spoken_text.replace(activator, "").strip()

            command_found = False

            if 'выключи компьютер' in spoken_text:
                os.system("shutdown /s /t 1")
                command_found = True
                logging.info("Компьютер выключается.")
            elif 'перезагрузка' in spoken_text or 'перезагрузка компьютера' in spoken_text:
                os.system("shutdown /r /t 1")
                command_found = True
                logging.info("Компьютер перезагружается.")
            elif 'спящий режим' in spoken_text or 'спи' in spoken_text:
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                command_found = True
                logging.info("Компьютер переходит в спящий режим.")
            elif 'очисти корзину' in spoken_text:
                os.system("echo Y | PowerShell.exe Clear-RecycleBin")
                command_found = True
                logging.info("Корзина очищена.")
            elif 'скриншот' in spoken_text or 'сделай скриншот' in spoken_text:
                os.system("nircmd.exe savescreenshot \"screenshot.png\"")
                command_found = True
                logging.info("Скриншот сохранён как 'screenshot.png'.")
            elif 'открой проводник' in spoken_text or 'проводник' in spoken_text:
                os.startfile('explorer.exe')
                command_found = True
                logging.info("Открываю проводник.")
            elif 'открой калькулятор' in spoken_text or 'калькулятор' in spoken_text:
                os.startfile('calc.exe')
                command_found = True
                logging.info("Открываю калькулятор.")
            elif 'пауза' in spoken_text or 'воспроизведения' in spoken_text or 'воспроизведение' in spoken_text:
                keyboard.press(Key.media_play_pause)
                command_found = True
                logging.info("Пауза.")
            elif 'предыдущее видео' in spoken_text:
                os.system("nircmd.exe sendkeypress ctrl+left")
                command_found = True
                logging.info("Предыдущее видео.")
            elif 'новая вкладка' in spoken_text or 'вкладка' in spoken_text:
                os.system("nircmd.exe sendkeypress ctrl+t")
                command_found = True
                logging.info("Открываю новую вкладку.")
            elif 'инкогнито' in spoken_text:
                os.system("nircmd.exe sendkeypress ctrl+shift+n")
                command_found = True
                logging.info("Открываю режим инкогнито.")
            elif 'закрой' in spoken_text or 'закрой окно' in spoken_text:
                os.system("nircmd.exe sendkeypress alt+f4")
                command_found = True
                logging.info("Закрываю окно.")
            elif 'найди' in spoken_text:
                search_query = spoken_text.replace('найди', '').strip()
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
                logging.info(f"Ищу в интернете: {search_query}")
                command_found = True
            elif 'открой браузер' in spoken_text:
                webbrowser.open("https://")
                command_found = True
                logging.info("Открываю браузер.")
            elif 'сделай скриншот' in spoken_text:
                os.system("nircmd.exe savescreenshot \"screenshot.png\"")
                command_found = True
                logging.info("Скриншот сделан и сохранён.")
            elif 'выключи звук' in spoken_text:
                os.system("nircmd.exe mutesysvolume 1")
                command_found = True
                logging.info("Звук выключен.")
            elif 'включи звук' in spoken_text:
                os.system("nircmd.exe mutesysvolume 0")
                command_found = True
                logging.info("Звук включён.")
            elif 'открой диспетчер задач' in spoken_text:
                os.system("taskmgr")
                command_found = True
                logging.info("Открываю диспетчер задач.")
            elif 'заблокируй компьютер' in spoken_text:
                os.system("rundll32.exe user32.dll,LockWorkStation")
                command_found = True
                logging.info("Компьютер заблокирован.")
            elif 'открой блокнот' in spoken_text or 'блокнот' in spoken_text:
                os.system("notepad")
                command_found = True
                logging.info("Открываю блокнот.")
            elif 'мышь направо' in spoken_text:
                pg.move(50, 0, 0.5)
                command_found = True
                logging.info("Перемещаю мышь на право.")
            elif 'мышь налево' in spoken_text:
                pg.move(50, 0, 0.5)
                command_found = True
                logging.info("Перемещаю мышь на лево.")
            elif 'мышь вверх' in spoken_text:
                pg.move(0, -50, 0.5)
                command_found = True
                logging.info("Перемещаю мышь на верх.")
            elif 'мышь вверх два' in spoken_text:
                pg.move(0, -500, 0.2)
                command_found = True
                logging.info("Перемещаю мышь на верх 2.")
            elif 'мышь вниз' in spoken_text:
                pg.move(0, +50, 0.5)
                command_found = True
                logging.info("Перемещаю мышь на вниз.")
            elif 'мышь вниз два' in spoken_text:
                pg.move(0, +500, 0.2)
                command_found = True
                logging.info("Перемещаю мышь на вниз 2.")
            elif 'клик' in spoken_text or 'нажми' in spoken_text or 'кликни' in spoken_text:
                pg.leftClick()
                command_found = True
                logging.info("Кликаю.")
            elif 'выдели' in spoken_text or 'выдели всё' in spoken_text:
                os.system("nircmd.exe sendkeypress ctrl+a")
                command_found = True
                logging.info("Выделяю текст.")
            elif spoken_text.startswith('види '):
                text_to_type = spoken_text.replace('види ', '', 1).strip()

                logging.info(f"Тип переменной text_to_type: {type(text_to_type)}")
                logging.info(f"Содержимое text_to_type: '{text_to_type}'")

                for char in text_to_type:
                  keyboard.press(char)
                  keyboard.release(char)
                  time.sleep(0.1)
                command_found = True
                logging.info(f"Введён текст: {text_to_type}")
            elif 'удали' in spoken_text:
                os.system("nircmd.exe sendkeypress delete")
                command_found = True
                logging.info("Удаляю текст.")
            elif 'скопируй' in spoken_text:
                os.system("nircmd.exe sendkeypress ctrl+c")
                command_found = True
                logging.info("Копирую текст текст.")
            elif 'вставь' in spoken_text:
                os.system("nircmd.exe sendkeypress ctrl+v")
                command_found = True
                logging.info("Вставляю текст.")
            elif 'открой ютуб' in spoken_text or 'запусти ютуб' in spoken_text:
                webbrowser.open("https://www.youtube.com")
                command_found = True
                logging.info("Открываю YouTube.")
            elif 'включи новогоднюю музыку' in spoken_text or 'открой новогоднюю музыку' in spoken_text:
                webbrowser.open("https://www.youtube.com/watch?v=TY2eYw-48Bo&ab_channel=JoshuaLawter")
                command_found = True
                logging.info("Открываю новогоднюю музыку.")
            elif 'что такое' in spoken_text or 'объясни' in spoken_text:
                query = spoken_text.replace('что такое', '').strip()
                webbrowser.open(f"https://ru.wikipedia.org/wiki/{query}")
                command_found = True
                logging.info(f"Ищу в Википедии: {query}.")
            elif 'переведи' in spoken_text:
                text_to_translate = spoken_text.replace('переведи', '').strip()
                webbrowser.open(f"https://translate.google.com/?sl=auto&tl=ru&text={text_to_translate}")
                command_found = True
                logging.info(f"Перевод текста: {text_to_translate}.")
            elif 'кем ты разработан' in spoken_text or 'кто твой разработчик' in spoken_text:
                webbrowser.open("https://github.com/CatDevCode")
                command_found = True
                logging.info("Открываю страницу с информацией о разработчике.")
            elif 'погода' in spoken_text or 'открой погоду' in spoken_text:
                webbrowser.open("https://yandex.ru/pogoda")
                command_found = True
                logging.info("Открываю погоду.")
            elif 'сохрани' in spoken_text or 'сохрани текст' in spoken_text:
                os.system("nircmd.exe sendkeypress ctrl+s")
                command_found = True
                logging.info("Сохраняю файл.")
            elif 'сверни окно' in spoken_text or 'сверни' in spoken_text:
                os.system("nircmd.exe win min foreground")
                command_found = True
                logging.info("Сворачиваю активное окно.")
            elif 'сайт кота' in spoken_text or 'открой сайт кота' in spoken_text:
                webbrowser.open("https://catdevcode.github.io/KOT-website/")
                command_found = True
                logging.info("Открываю сайт кота.")
            elif 'поверх всех окон' in spoken_text or 'помести себя поверх всех окон' in spoken_text:
                self.cat_widget.root.attributes("-topmost", True)
                command_found = True
                logging.info("Кот теперь поверх всех окон.")
                print("Кот теперь поверх всех окон.")
            elif 'убери себя поверх окон' in spoken_text:
                self.cat_widget.root.attributes("-topmost", False)
                command_found = True
                logging.info("Кот убран с переднего плана.")
                print("Кот убран с переднего плана.")
            else:
                if spoken_text in self.custom_commands:
                    actions = self.custom_commands[spoken_text]
                    for action in actions:
                        os.system(action)
                    command_found = True
                    logging.info(f"Выполняю пользовательскую команду: {spoken_text} -> {actions}")

            if command_found:
                self.cat_widget.open_mouth() 
                success_sound.play()
                print("Команда выполнена.")
            else:
                self.cat_widget.open_mouth()
                failure_sound.play()
                logging.warning("Команда не распознана.")
                print("Команда не распознана.")

    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.mic.terminate()
        logging.info("Ассистент остановлен.")


def main():
    assistant = VoiceAssistant()
    thread = threading.Thread(target=assistant.recognize_speech_from_mic)
    thread.start()

    assistant.cat_widget.root.mainloop()

if __name__ == "__main__":
    main()

