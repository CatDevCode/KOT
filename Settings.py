import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess

COMMANDS_FILE = 'custom_commands.json'

class Launcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Настройки для KOT-a")
        self.root.geometry("780x590")
        self.root.configure(bg="#575757")

        style = ttk.Style()
        style.theme_use('clam')

        # Настройка стилей
        style.configure("Treeview",
                        background="#575757",
                        foreground="#FFFFFF",
                        rowheight=25,
                        fieldbackground="#575757")
        style.map("Treeview",
                  background=[("selected", "#0078D4")],
                  foreground=[("selected", "white")])

        # Настройка стиля для скроллбара
        style.configure("Vertical.TScrollbar",
                        gripcount=0,
                        background="#4A4A4A",
                        darkcolor="#4A4A4A",
                        lightcolor="#4A4A4A",
                        troughcolor="#575757",
                        bordercolor="#575757",
                        arrowcolor="#FFFFFF")
        style.map("Vertical.TScrollbar",
                  background=[("active", "#0078D4")],
                  troughcolor=[("active", "#575757")])

        # Установка шрифта Roboto
        style.configure("Header.TLabel", font=("Roboto", 16, "bold"), background="#575757", foreground="#FFFFFF")
        style.configure("TButton", font=("Roboto", 10, "bold"), padding=8, background="#4A4A4A", foreground="#FFFFFF")
        style.map("TButton", background=[("active", "#0078D4")])  # Цвет кнопки при наведении

        style.configure("TEntry", font=("Roboto", 10), padding=5, fieldbackground="#575757", foreground="#FFFFFF")

        # Заголовок
        self.header_label = ttk.Label(root, text="Настройки для KOT-а", style="Header.TLabel")
        self.header_label.pack(pady=10)

        # Инструкция
        self.label = ttk.Label(root, text="1: Введите команду. 2: Введите действие (действие будет выполняться как в консоли).", 
                                background="#575757", foreground="#FFFFFF")
        self.label.pack(pady=5)

        self.lol = ttk.Label(root, text="Если нужно выполнить два действия, команды вводите через запятую в скобках, например: (python command1.py, python command2.py).", 
                                background="#575757", foreground="#FFFFFF")
        self.lol.pack(pady=5)

        # Создаем фрейм для Treeview
        self.tree_frame = tk.Frame(root, bg="#4A4A4A", bd=2, relief=tk.RAISED)  # Изменили цвет фона фрейма
        self.tree_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Создаем Treeview для отображения команд
        self.tree = ttk.Treeview(self.tree_frame, columns=("Command", "Actions"), show='headings', height=10)
        self.tree.heading("Command", text="Команда")
        self.tree.heading("Actions", text="Действия")
        self.tree.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        # Добавляем скроллбар для Treeview
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview, style="Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Фрейм для ввода
        self.entry_frame = tk.Frame(root, bg="#575757")
        self.entry_frame.pack(pady=10)

        self.command_entry = ttk.Entry(self.entry_frame, width=25)
        self.command_entry.grid(row=0, column=0, padx=5)

        self.actions_entry = ttk.Entry(self.entry_frame, width=30)
        self.actions_entry.grid(row=0, column=1, padx=5)

        self.add_button = ttk.Button(self.entry_frame, text="Добавить", command=self.add_command)
        self.add_button.grid(row=0, column=2, padx=5)

        # Кнопка для удаления команд
        self.delete_button = ttk.Button(self.entry_frame, text="Удалить", command=self.delete_command)
        self.delete_button.grid(row=0, column=3, padx=5)

        self.start_button = ttk.Button(root, text="Запустить KOT-a", command=self.launch_kot)
        self.start_button.pack(pady=10)

        self.load_commands()

    def load_commands(self):
        if os.path.exists(COMMANDS_FILE):
            with open(COMMANDS_FILE, 'r', encoding='utf-8') as f:
                commands = json.load(f)
                for cmd, actions in commands.items():
                    self.tree.insert("", tk.END, values=(cmd, ", ".join(actions)))

    def save_commands(self):
        commands = {}
        for row in self.tree.get_children():
            cmd, actions = self.tree.item(row, 'values')
            commands[cmd] = actions.split(', ')
        with open(COMMANDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(commands, f, ensure_ascii=False, indent=4)

    def add_command(self):
        cmd = self.command_entry.get().strip()
        actions = self.actions_entry.get().strip()
        if cmd and actions:
            self.tree.insert("", tk.END, values=(cmd, actions))
            self.command_entry.delete(0, tk.END)
            self.actions_entry.delete(0, tk.END)
            self.save_commands()  # Сохраняем команды при добавлении
        else:
            messagebox.showwarning("KOT", "Пожалуйста, заполните все поля.")

    def delete_command(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)
            self.save_commands()  # Обновляем файл после удаления
        else:
            messagebox.showwarning("KOT", "Пожалуйста, выберите команду для удаления.")

    def launch_kot(self):
        self.save_commands()  # Сохраняем команды перед запуском
        subprocess.Popen(['python', 'KOT.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)
        self.root.quit()  # Закрываем лаунчер

if __name__ == "__main__":
    root = tk.Tk()
    launcher = Launcher(root)
    root.mainloop()
