import subprocess
import os
import sys

if getattr(sys, 'frozen', False):
    current_directory = os.path.dirname(sys.executable)
else:
    current_directory = os.path.dirname(os.path.abspath(__file__))


kot_file = os.path.join(current_directory, 'kot.py')


try:
    subprocess.run(['start', 'cmd', '/k', 'python', kot_file], shell=True)
except Exception as e:
    print(f'Ошибка при попытке открыть новую консоль: {e}')
