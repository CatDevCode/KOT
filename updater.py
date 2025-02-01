import requests
import os
import webbrowser
import time
# Для включение отладки через консоль напишите в debug пустое значение "", чтобы отключить напишите "cls"
debug = "cls"



class VersionChecker:
    def __init__(self, url, current_version):
        self.url = url
        self.current_version = current_version
    
    def show_update_info(self):
        try:
             otvet = int(input("Введите 1 для открытия сайта для установки. Или 0 для выхода -->"))
     
             if otvet == 1:
                 webbrowser.open("https://github.com/CatDevCode/KOT")
             elif otvet == 0:
                 exit()
             else:
                 print("Неверный ввод. Попробуйте снова.")
                 self.check_for_updates()
        except ValueError:
             os.system(debug)
             print("-" * 50)
             print("Введено неверное значение. Жду 4 секунд чтобы ты прочитал")
             print("-" * 50)
             time.sleep(4)
             self.check_for_updates()
        
        

    def get_version(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            print("Debug: Проверка github(200 - норма): ", response)
            line = response.text.splitlines()[0]
            print("Debug: Строка версии: ", line)
            version = line.split('=')[1].strip().strip('"')
            print("Debug: Полученная версия: ",version)

            return version
        except requests.exceptions.HTTPError as http_err:
            os.system(debug)
            print("!" * 50)
            print(f"HTTP ошибка: {http_err}")
            print("!" * 50)
        except Exception as err:
            os.system(debug)
            print("!" * 50)
            print(f"Ошибка: {err}")
            print("!" * 50)
        return None


    def check_for_updates(self):
        latest_version = self.get_version()
        if latest_version:
            if latest_version != self.current_version:
                os.system(debug)
                print("-" * 50)
                print("\n")
                print(f"Обновление доступно! Последняя версия: {latest_version}, ваша версия: {self.current_version}")
                print("\n")
                print("-" * 50)
                self.show_update_info()

            else:
                os.system(debug)
                print("-" * 50)
                print("Вы используете последнюю версию.")
                print("-" * 50)
                input("Нажмите Enter для выхода.")
                exit()
        else:
            os.system(debug)
            print("-" * 50)
            print("\n")
            print("Не удалось получить информацию о версии.")
            print("\n")
            print("-" * 50)

url = "https://raw.githubusercontent.com/CatDevCode/KOT/refs/heads/main/KOT.py"
print("Debug: Cыллка: ", url)
current_version = "0.2.8"
print("Debug: Версия установленная: ", current_version)
checker = VersionChecker(url, current_version)
print("Debug: checker: ", checker)
checker.check_for_updates()
