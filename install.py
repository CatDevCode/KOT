import os
import time
print("-" * 90)
print("█▀▀█  █   █ 　  █▀▀█  █▀▀█ ▀▀█▀▀ 　  █▀▀▄  █▀▀▀  █   █ 　  █▀▀█  █▀▀▀█  █▀▀▄  █▀▀▀ 　 ▄ ▀▄ ")
print("█▀▀▄  █▄▄▄█ 　  █     █▄▄█   █   　  █  █  █▀▀▀   █ █  　  █     █   █  █  █  █▀▀▀ 　    █ ")
print("█▄▄█    █   　  █▄▄█  █  █   █   　  █▄▄▀  █▄▄▄   ▀▄▀  　  █▄▄█  █▄▄▄█  █▄▄▀  █▄▄▄ 　 ▀ ▄▀ ")
print("-" * 90)
time.sleep(3)
print("\n")
print("Начало установки: Установка необходимых пакетов:")
print("\n")
print("-" * 50)

os.system("pip install requests")

import subprocess
import sys
import requests
import zipfile

libraries = [
    "pyaudio",
    "vosk",
    "pygame",
    "Pillow",
    "pyautogui",
    "gtts",
    "pydub",
    "pynput"
]
print("-" * 90)
for library in libraries:
    subprocess.check_call([sys.executable, "-m", "pip", "install", library])
    print("-" * 90)

def download_file(url, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        start_time = time.time()

        with open(filename, 'wb') as file:
            for data in response.iter_content(chunk_size=1024):
                downloaded_size += len(data)
                file.write(data)

                elapsed_time = time.time() - start_time
                if elapsed_time > 0:
                    speed = downloaded_size / (1024 * elapsed_time)
                    speed_mb = speed / 1024
                else:
                    speed_mb = 0

                percent = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                print(f"\rЗагрузка: {percent:.2f}% | Загружено: {downloaded_size / (1024 * 1024):.2f} MB | Скорость: {speed_mb:.2f} MB/s", end='')

        print("\nФайл успешно загружен.")
    except requests.exceptions.RequestException as e:
        print(f"\nОшибка при загрузке файла: {e}")

def extract_zip(filename, extract_to):
    try:
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Файл {filename} успешно извлечён в {extract_to}.")
    except zipfile.BadZipFile:
        print("Ошибка: файл не является корректным ZIP-архивом.")
        print("--> main")
        main()
    except Exception as e:
        print(f"Ошибка при извлечении файла: {e}")
        print("--> main")
        main()

def main():
    print("\n")
    print("Выберите голосовую модель для загрузки:")
    print("1. Более продвинутая версия (ОЧЕНЬ требовательная),(ДОЛГО ЗАГРУЖАЕТСЯ) 40 - 60 сек")
    print("2. Более простая версия (работает на слабых и средних компьютерах),(Быстро загружаеться) 5 - 10 сек")
    choice = input("Введите голосовую модель (1 или 2) --> ")

    print("\n")

    if choice == '1':
        url = "https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip"
        filename = "vosk.zip"
    elif choice == '2':
        url = "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"
        filename = "vosk.zip"
    else:
        print("-" * 45)
        print("Неверный выбор. Пожалуйста, выберите 1 или 2. --> main")
        print("-" * 45)
        main()

    print("-" * 50)
    print("Идет скачивание голосовой модели vosk")
    print("-" * 50)

    print("\n")

    current_directory = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_directory, filename)

    download_file(url, full_path)


    extract_zip(full_path, current_directory)

    extracted_folder_name = None
    for item in os.listdir(current_directory):
        if item.startswith("vosk-model"):
            extracted_folder_name = item
            break

    if extracted_folder_name:
        final_dir = os.path.join(current_directory, "vosk")
        if os.path.exists(final_dir):
            print("-" * 50)
            print(f"Папка '{final_dir}' уже существует. Удаление...")
            print("-" * 50)
            import shutil
            shutil.rmtree(final_dir)


        os.rename(os.path.join(current_directory, extracted_folder_name), final_dir)
    else:
        print("Ошибка: не удалось найти извлеченную папку.")
        print("Попробуйте заново --> main")
        main()

    if os.path.exists(full_path):
        os.remove(full_path)
    


    os.system("cls")

    print("\n")
    print("-" * 45)
    print("\n")
    print("Приятного использования KOT-а!")
    print("\n")
    print("-" * 45)
    print("Выход через 5 секунд")
    time.sleep(5)

if __name__ == "__main__":
    main()
