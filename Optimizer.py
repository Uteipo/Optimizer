import psutil
import winreg
import tkinter as tk 
import subprocess
from tkinter import ttk 
from tkinter import messagebox
import os 
import shutil
root = tk.Tk()
root.title('Optimizer')
root.geometry('450x550')
root.configure(bg='#1e1e1e')
style = ttk.Style()
style.theme_use('clam')
style.configure('TNotebook', background='#1e1e1e', borderwidth=0)
style.configure('TFrame', background='#1e1e1e')
style.configure('TNotebook.tab', background = '#1e1e1e', borderwidht=0)
style.map('TNotebook.Tab', background=[('selected', '#0078d7')])
style.configure('TButton', background='#2d2d2d', foreground='white', borderwidth=1)
style.map('TButton', background=[('active', '#3e3e3e')])
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx= 10, pady= 10)
tab1 = ttk.Frame(notebook)
ram_bar = ttk.Progressbar(tab1, orient='horizontal', length=300, mode='determinate')
ram_label = tk.Label(tab1, text='Оперативная память', bg='#1e1e1e', fg='white')
ram_label.pack(pady=10)
ram_bar.pack(pady=5)
cpu_label = tk.Label(tab1, text='Процессор', bg='#1e1e1e', fg='white')
cpu_bar = ttk.Progressbar(tab1, orient='horizontal', length=300, mode='determinate')
cpu_label.pack(pady=10)
cpu_bar.pack(pady=5)
disk = []
for part in psutil.disk_partitions():
    disk_label = tk.Label(tab1, text=f'Диск {part.device}',bg='#1e1e1e', fg='white')
    disk_bar = ttk.Progressbar(tab1, orient='horizontal', length=300, mode='determinate')
    disk_label.pack(pady=5)
    disk_bar.pack(pady=5)
    disk.append((part.device, disk_label, disk_bar))
def update_stats():
    memory = psutil.virtual_memory()
    used_gb = memory.used / (1024**3)
    total_gb = memory.total / (1024**3)
    ram_bar['value'] = memory.percent
    ram_label.config(
    text=f'Память: {used_gb:.1f} / {total_gb:.1f} ГБ {memory.percent}%')
    cpu = psutil.cpu_percent()
    cpu_bar['value'] = cpu
    cpu_label.config(text=f'Процессор: {cpu}%')
    for device, label, bar in disk:
            usage = psutil.disk_usage(device)
            disk_used = usage.used / (1024**3)
            total_gb = usage.total / (1024**3)
            bar['value'] = usage.percent
            label.config(text=f'Диск {device}: {disk_used:.1f} / {total_gb:.1f} ГБ ({usage.percent}%)')
    root.after(1000, update_stats)
update_stats()
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
notebook.add(tab1, text= 'Обзор')
notebook.add(tab2, text= 'Мусор')
notebook.add(tab3, text= 'Автозагрузка')
def clear_junk():
    temp_dir = os.environ.get('TEMP', '')
    deleted_count = 0
    for item in os.listdir(temp_dir):
        full_path = os.path.join(temp_dir, item)
        try:
            if os.path.isfile(full_path):
                os.remove(full_path)
                deleted_count += 1
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)
                deleted_count += 1
        except Exception:
            pass
    messagebox.showinfo('Готово', f'Удалено объектов: {deleted_count}')
junk_label = tk.Label(tab2, text='Очистка временных файлов (TEMP)', bg='#1e1e1e', fg='white')
junk_label.pack(pady=10)
junk_button = tk.Button(tab2, text='Очистить мусор', command=clear_junk, bg='#1e1e1e', fg='white')
junk_button.pack(pady=10)
auto_label = tk.Label(tab3, text='Программы в автозагрузке', bg='#1e1e1e', fg='white')
auto_label.pack(pady=10)
auto_listbox = tk.Listbox(tab3, width=50, height=12)
auto_listbox.pack(pady=5, padx=10)
def load_startup():
    auto_listbox.delete(0, tk.END)
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run')
    try:
        approved_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run' )
    except FileNotFoundError:
        approved_key = None
    for i in range(winreg.QueryInfoKey(key)[1]):
        name = winreg.EnumValue(key, i)[0]
        status = '[ВКЛ]'
        if approved_key:
            try:
                data, _ = winreg.QueryValueEx(approved_key, name)
                if data[0] % 2 == 1:
                    status = '[ОТКЛ]'
            except FileNotFoundError:
                pass
        auto_listbox.insert(tk.END, f'{status} {name}')
    winreg.CloseKey(key)
    if approved_key:
        winreg.CloseKey(approved_key)
def toggle_startup(enable):
        selection = auto_listbox.curselection()
        if not selection:
            return
        text = auto_listbox.get(selection)
        app_name = text.split(' ', 1)[1]
        if enable:
            data = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        else:
            data = b'\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'     
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run')
        winreg.SetValueEx(key, app_name, 0, winreg.REG_BINARY, data)
        winreg.CloseKey(key)
        load_startup()
load_startup()
enable_btn = tk.Button(tab3, text='Включить', command=lambda: toggle_startup(True))
enable_btn.pack(pady=5)
disable_btn = tk.Button(tab3, text='Отключить', command=lambda: toggle_startup(False))
disable_btn.pack(pady=5)
def enable_ultimate_power():
    subprocess.run(['powercfg', '-duplicatescheme', 'e9a42b02-d5df-448d-aa00-03f14749eb61'], creationflags=subprocess.CREATE_NO_WINDOW)
    messagebox.showinfo('Готово', 'Схема «Максимальная производительность» добавлена!\nВключите её в Панели управления -> Электропитание.')
power_btn = ttk.Button(tab2, text='Макс. производительность', command=enable_ultimate_power)
power_btn.pack(pady=10)
root.mainloop()
