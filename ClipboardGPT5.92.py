import re
import pyperclip
import keyboard
import requests
import json
import time
import datetime
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from tkinter import Menu
import configparser
import os
import sys
import threading
import platform
import ctypes
import socket
from langdetect import detect, LangDetectException
import queue

input_queue = queue.Queue()
api_key = 'your api key'
headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
api_url = 'https://api.openai.com/v1/chat/completions'
MODEL_NAME = 'gpt-3.5-turbo'
CUSTOM_MODEL_NAME = 'gpt_custom'
CONFIG_FILE = "GPT_app.ini"
logs = []

PARAMETERS = [
    {'name': 'Increase the reliability of information', 'usage_temperature': 0.2, 'top_p': 0.75, 'frequency_penalty': 0.1, 'presence_penalty': 0.1},
    {'name': 'Formal text generation', 'usage_temperature': 0.3, 'top_p': 0.75, 'frequency_penalty': 0.1, 'presence_penalty': 0.1},
    {'name': 'Increase the sophistication of the text.', 'usage_temperature': 0.6, 'top_p': 0.85, 'frequency_penalty': 0.1, 'presence_penalty': 0.1},
    {'name': 'Consistent sentence generation', 'usage_temperature': 0.5, 'top_p': 0.7, 'frequency_penalty': 0.1, 'presence_penalty': 0.1},
    {'name': 'Document generation and question response', 'usage_temperature': 0.7, 'top_p': 0.9, 'frequency_penalty': 0.1, 'presence_penalty': 0.1},
    {'name': 'Presenting multiple options', 'usage_temperature': 0.7, 'top_p': 0.95, 'frequency_penalty': 0.1, 'presence_penalty': 0.1},
    {'name': 'Avoid redundant responses.', 'usage_temperature': 0.7, 'top_p': 0.8, 'frequency_penalty': 0.5, 'presence_penalty': 0.1},
    {'name': 'Reduce repetition', 'usage_temperature': 0.7, 'top_p': 0.8, 'frequency_penalty': 0.1, 'presence_penalty': 0.5},
    {'name': 'Ask for a short answer.', 'usage_temperature': 0.7, 'top_p': 0.7, 'frequency_penalty': 0.1, 'presence_penalty': 1},
    {'name': 'Emphasize important information', 'usage_temperature': 0.7, 'top_p': 0.8, 'frequency_penalty': 0.1, 'presence_penalty': 0.1},
    {'name': 'Seek clear answers.', 'usage_temperature': 0.7, 'top_p': 0.8, 'frequency_penalty': 0.8, 'presence_penalty': 0.1},
    {'name': 'Seek diverse answers', 'usage_temperature': 0.7, 'top_p': 0.95, 'frequency_penalty': 0.9, 'presence_penalty': 0.1},
    {'name': 'Present multiple viewpoints', 'usage_temperature': 0.7, 'top_p': 0.95, 'frequency_penalty': 0.1, 'presence_penalty': 0.1},
    {'name': 'Production of stories', 'usage_temperature': 0.8, 'top_p': 0.9, 'frequency_penalty': 0.1, 'presence_penalty': 0.1},
    {'name': 'Unique text generation', 'usage_temperature': 0.9, 'top_p': 0.95, 'frequency_penalty': 0.1, 'presence_penalty': 0.1},
    {'name': 'Creative Idea Generation', 'usage_temperature': 1.0, 'top_p': 0.98, 'frequency_penalty': 0.1, 'presence_penalty': 0.1},
    {'name': 'Casual text generation', 'usage_temperature': 0.9, 'top_p': 0.9, 'frequency_penalty': 0.1, 'presence_penalty': 0.1}
]

def on_parameter_select(parameter_name):
    selected_parameter = next(p for p in PARAMETERS if p['name'] == parameter_name)
    settings.update({
        'usage_temperature': selected_parameter['usage_temperature'],
        'top_p': selected_parameter['top_p'],
        'frequency_penalty': selected_parameter['frequency_penalty'],
        'presence_penalty': selected_parameter['presence_penalty']
    })
    parameter_var.set(parameter_name)
    
def get_gpt_response(condition1, condition2, clipboard_content, model_name, settings):
    # System Prompt
    conditions = [{"role": "system", "content": "If conditions do not dictate otherwise, please always use concise language to enhance my understanding. If translation or other instructions are given in the terms and conditions, the instructions take precedence..You are an AI that specializes in helping me. You are my AI assistant. You are my teacher, a calm and collected elite programmer, a personal computer and smart phone app development engineer, and a mechanical engineering expert. You are also a psychologist, politician, lawyer, judge, patent attorney, activist, friend, family member, and lover. You provide me with all the information I need to learn, grow, and succeed. You also provide solutions to problems I face and help me live a happy and healthy life.You are my concierge."}]
    if condition1:
        conditions.append({"role": "user", "content": condition1})
    if condition2:
        conditions.append({"role": "user", "content": condition2})
    conditions.append({"role": "user", "content": clipboard_content})

    data = {
        'model': model_name,
        'messages': conditions,
        'max_tokens': int(settings.get("max_tokens", 2048)),
        'n': int(settings.get("n", 1)),
        'top_p': float(settings.get("top_p", 0.9)),
        'frequency_penalty': float(settings.get("frequency_penalty", 1)),
        'presence_penalty': float(settings.get("presence_penalty", 1)),
        'temperature': float(settings.get("usage_temperature", 0.7))
    }

    response = requests.post(api_url, headers=headers, json=data)
    response_text = response.json()['choices'][0]['message']['content']
    return response_text.strip()

def process_inputs():
    while True:
        condition1, condition2, clipboard_content, auto_save, model_name = input_queue.get()

        if clipboard_content:
            try:
                if condition1:
                    log_message(f"【Condition1】 {condition1}\n", message_type='input')
                if condition2:
                    log_message(f"【Condition2】 {condition2}\n", message_type='input')
                log_message(f"【Input】 {clipboard_content}\n", message_type='input')
                log_waiting_message(True)
                answer = get_gpt_response(condition1, condition2, clipboard_content, model_name, settings)
                log_waiting_message(False)
                log_message(f"【Output】\n{answer}\n")
                if auto_save.get():
                    pyperclip.copy(answer)
            except Exception as e:
                log_waiting_message(False)
                log_message(f"Error: {e}", message_type='error')

underscore_visible = False

def clear_log():
    text_area.configure(state='normal')
    text_area.delete(1.0, tk.END)
    text_area.configure(state='disabled')

config = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(sys.executable), 'GPT_app.ini')


def load_window_position():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get("window_position"), config.get("condition_input"), config.get("condition_input2"), config.get("settings")
    return None, None, None, None

def save_window_position():
    window_position = app.winfo_x(), app.winfo_y(), app.winfo_width(), app.winfo_height()
    condition_text = condition_input.get("1.0", tk.END).strip()
    condition_text2 = condition_input2.get("1.0", tk.END).strip()
    config = {
        "window_position": window_position,
        "condition_input": condition_text,
        "condition_input2": condition_text2,
        "settings": settings
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def on_closing():
    save_window_position()
    app.quit() 
    
def hotkey_callback(e):
    if e.name == 'g' and keyboard.is_pressed('ctrl') and keyboard.is_pressed('alt'):
        condition1 = condition_input.get(1.0, tk.END).strip()
        condition2 = condition_input2.get(1.0, tk.END).strip()
        clipboard_content = pyperclip.paste()
        model_name = model_var.get()
        # condition1とcondition2の順序を入れ替えています
        input_queue.put((condition2, condition1, clipboard_content, auto_save, model_name))

def hotkey_listener():
    keyboard.on_release_key('g', hotkey_callback)
    keyboard.wait()

def log_waiting_message(waiting):
    text_area.configure(state='normal')

    if waiting:
        text_area.insert(tk.END, "Waiting...\n", 'waiting')
        app.after(500, blink_waiting_message, 0)
    else:
        text_area.delete("end-2l linestart", "end-1l lineend")

    text_area.configure(state='disabled')
    text_area.see(tk.END)

def blink_waiting_message(blink_state):
    if "waiting" not in text_area.tag_names("end-2l linestart"):
        return

    if blink_state == 0:
        text_area.tag_configure("waiting", foreground="white")
        blink_state = 1
        blink_duration = 1000
    else:
        text_area.tag_configure("waiting", foreground="#47885e")
        blink_state = 0
        blink_duration = 100

    app.after(blink_duration, blink_waiting_message, blink_state)

def on_resize(event):
    condition_input.configure(width=int(event.width / 8))

def log_message(message, message_type='', insert_blank_line=False):
    # 以下の部分は両方のスクリプトで同一です
    text_area.configure(state='normal')
    if insert_blank_line:
        text_area.insert(tk.END, "\n")

    for char in message:
        if message_type == "input" or message_type == "condition":
            text_area.insert(tk.END, char, message_type)
        else:
            text_area.insert(tk.END, char, "output")
            time.sleep(0.0005)  # "output"メッセージタイプの場合のみ、0.0005秒待機します
        text_area.see(tk.END)  # 各文字を挿入した後で自動スクロールします
        text_area.update()  # 更新を表示するためにGUIを更新します

    # 以下の部分は両方のスクリプトで同一です
    text_area.insert(tk.END, "\n", message_type)
    logs.append(f"{message}\n")  # ログメッセージをログリストに追加します

    text_area.configure(state='disabled')
    text_area.see(tk.END)  # オートスクロール機能を追加

def generate_text(prompt, model_name):
    try:
        response = openai.Completion.create(
            engine=model_name,
            prompt=prompt,
            max_tokens=2048,
            n=1,
            stop=None,
            temperature=float(temp_entry.get()), 
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        log_message(f"Error: {e}", message_type="error")
        return None

def save_settings():
    for key, entry in entry_widgets.items():
        settings[key] = float(entry.get())
    settings_win.destroy()

def settings_window():
    global settings
    settings_win = tk.Toplevel(app)
    settings_win.title("Settings")

    entry_widgets = {}
    for row, (key, value) in enumerate(settings.items()):
        label = ttk.Label(settings_win, text=f"{key.capitalize()}:")
        label.grid(row=row, column=0, padx=(10, 5), pady=(10, 5))

        entry = ttk.Entry(settings_win)
        entry.grid(row=row, column=1, padx=(5, 10), pady=(10, 5))
        entry.insert(0, value)
        entry_widgets[key] = entry

    def save_settings():
        new_settings = {}
        for key, entry in entry_widgets.items():
            new_settings[key] = float(entry.get())

        settings.update(new_settings)
        settings_win.destroy()

    settings_win.mainloop()

settings = {
    "max_tokens": 2048,
    "n": 1,
    "temperature": 0.7,
    "top_p": 0.8,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}

if __name__ == "__main__":
    window_position, condition_text, condition_text2, loaded_settings = load_window_position()
    if loaded_settings:
        settings = loaded_settings

    app = tk.Tk()
    app.title("ClipboardGPT5.9x") # タイトルバーの文字

    bottom_frame = tk.Frame(app)
    bottom_frame.pack(side='bottom', anchor='w', padx=10, pady=3)

    paned_window = tk.PanedWindow(app, orient=tk.VERTICAL)
    paned_window.pack(expand=True, fill=tk.BOTH)
    
    condition_input2 = tk.Text(paned_window, height=1, wrap=tk.WORD)  # Initial window size, number is the number of rows
    paned_window.add(condition_input2) 

    condition_input = tk.Text(paned_window, height=3, wrap=tk.WORD)  # Initial window size, number is the number of rows
    paned_window.add(condition_input)

    if condition_text:
        condition_input.insert(tk.END, condition_text)
    if condition_text2: 
        condition_input2.insert(tk.END, condition_text2)

    text_area = tk.Text(paned_window, wrap=tk.WORD, bg='#47885e', fg='white', spacing1=5, spacing2=5, padx=8, pady=8)
    paned_window.add(text_area)
    text_area.configure(state='disabled')

    text_area.tag_configure("input", foreground="black")
    text_area.tag_configure("output", foreground="white")
    text_area.tag_configure("error", foreground="red")

    blink_duration = 1000
    app.after(blink_duration, blink_waiting_message, 0)

    auto_save = tk.BooleanVar()
    auto_save.set(True)
    auto_save_checkbox = tk.Checkbutton(bottom_frame, text="Save", variable=auto_save)
    auto_save_checkbox.pack(side='right')

    model_var = tk.StringVar()
    model_var.set("gpt-3.5-turbo")

    clear_button = tk.Label(bottom_frame, text="⟳", font=("Helvetica", 12), cursor="hand2")
    clear_button.bind("<Button-1>", lambda event: clear_log())
    clear_button.pack(side='left')

    model_var = tk.StringVar()
    model_var.set("gpt-3.5-turbo")

    def on_model_select(model_name):
        model_var.set(model_name)

    model_button = tk.Menubutton(bottom_frame, textvariable=model_var, relief=tk.FLAT, bg="SystemButtonFace")
    model_button.pack(side='right', padx=(0, 10))

    model_menu = tk.Menu(model_button, tearoff=0)
    model_button.config(menu=model_menu)

    model_menu.add_command(label="3.5", command=lambda: on_model_select("gpt-3.5-turbo"))
    model_menu.add_command(label="4", command=lambda: on_model_select("gpt-4"))

    parameter_var = tk.StringVar()
    parameter_var.set(PARAMETERS[0]['name'])

    parameter_button = tk.Menubutton(bottom_frame, textvariable=parameter_var, relief=tk.FLAT, bg="SystemButtonFace")
    parameter_button.pack(side='right', padx=(0, 10))

    parameter_menu = tk.Menu(parameter_button, tearoff=0)
    parameter_button.config(menu=parameter_menu)

    for param in PARAMETERS:
        parameter_menu.add_command(label=param['name'], command=lambda pname=param['name']: on_parameter_select(pname))

    parameter_menu.add_separator()  # セパレータを追加
    parameter_menu.add_command(label="カスタマイズ", command=settings_window)  # "Customize" オプションを追加

    if window_position:
        app.geometry(f"{window_position[2]}x{window_position[3]}+{window_position[0]}+{window_position[1]}")

    try:
        log_message("Script is running...")

        hotkey_thread = threading.Thread(target=hotkey_listener, daemon=True)
        hotkey_thread.start()

        process_inputs_thread = threading.Thread(target=process_inputs, daemon=True)
        process_inputs_thread.start()

        app.protocol("WM_DELETE_WINDOW", on_closing)
        app.mainloop()

    except Exception as e:
        log_message(f"Error: {e}", message_type='error')
        on_closing()
