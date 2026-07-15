import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import copy
from modules.editor_sub import editor_engine

# Ссылка на общий буфер обмена для копирования деталей ЧПУ
EDITOR_CLIPBOARD = None

def get_resource_path(relative_path):
    """Определитель путей к файлам для разработки и для сборки в .exe"""
    import sys
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def create_toolbar_button(parent, icon_filename, default_text, command_func=None):
    """
    Ищет PNG в папке icons. Если файла нет — гарантированно выводит 
    аккуратную текстовую кнопку, чтобы фреймы не скрывались на Toolbar.
    """
    icon_path = get_resource_path(os.path.join("icons", icon_filename))
    
    # Специфические настройки для ровных текстовых кнопок на Toolbar
    btn_kwargs = {
        "text": default_text,
        "bg": "#ffffff", 
        "bd": 1, 
        "relief": tk.GROOVE, 
        "padx": 6, 
        "pady": 3, 
        "cursor": "hand2",
        "font": ("Arial", 9)
    }
    if command_func: 
        btn_kwargs["command"] = command_func
        
    if os.path.exists(icon_path):
        try:
            img = tk.PhotoImage(file=icon_path)
            btn = tk.Button(parent, image=img, bg="#ffffff", bd=1, relief=tk.GROOVE, cursor="hand2")
            btn.image = img 
            if command_func:
                btn.config(command=command_func)
            return btn
        except Exception: 
            pass
            
    # Если картинки в папке icons нет — возвращаем кнопку с четким текстом
    return tk.Button(parent, **btn_kwargs)

def build_toolbar(toolbar, canvas, state):
    """Собирает Блоки 1, 2 и 3 верхней горизонтальной панели инструментов"""
    global EDITOR_CLIPBOARD

    import json # Системный импорт для работы со словарями проекта

    # --- СЕКЦИЯ 1: УПРАВЛЕНИЕ ПРОЕКТАМИ ЧПУ (БЛОК 1) ---
    files_group = tk.Frame(toolbar, bg="#eaeaea")
    files_group.pack(side=tk.LEFT, padx=3, pady=2)

    def action_new_project():
        """Сброс сессии и очистка холста станка ЧПУ"""
        state["selected_id"] = None
        state["project_path"] = None
        state["pan_x"], state["pan_y"] = 0, 0
        state["scale"] = 100.0
        canvas.delete("drawn_line", "vector_text", "dxf_group")
        editor_engine.DRAWN_ELEMENTS = []
        editor_engine.HISTORY_REDO = []
        editor_engine.draw_editor_grid(canvas, canvas.winfo_width(), canvas.winfo_height(), 10, 0, 0)

    def action_open_project():
        """Чтение и разворачивание файла проекта .cam на координатном столе"""
        f_path = filedialog.askopenfilename(filetypes=[("Проект ЧПУ", "*.cam"), ("Все файлы", "*.*")])
        if not f_path: return
        try:
            with open(f_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # 1. Тотальный сброс текущего экрана
            action_new_project()
            
            # 2. Восстановление метаданных чертежа
            state["project_path"] = f_path
            state["pan_x"] = data.get("project_meta", {}).get("pan_x", 0)
            state["pan_y"] = data.get("project_meta", {}).get("pan_y", 0)
            state["scale"] = data.get("project_meta", {}).get("scale", 100.0)
            
            # 3. Восстановление настроек режимов резания
            if "cnc_settings" in data:
                editor_engine.CNC_SETTINGS.update(data["cnc_settings"])
                
            # 4. Заполнение системной памяти векторов ЧПУ
            editor_engine.DRAWN_ELEMENTS = data.get("geometry", [])
            
            # 5. Прорисовка векторов на миллиметровке станка
            for elem in editor_engine.DRAWN_ELEMENTS:
                if elem["type"] == "line":
                    elem["id"] = canvas.create_line(*elem["coords"], fill="#1d4182", width=2, tags="drawn_line")
                elif elem["type"] == "rect":
                    elem["id"] = canvas.create_rectangle(*elem["coords"], outline="#1d4182", width=2, tags="drawn_line")
                elif elem["type"] == "oval":
                    elem["id"] = canvas.create_oval(*elem["coords"], outline="#1d4182", width=2, tags="drawn_line")
            
            # Обновляем миллиметровую сетку под новые координаты панорамы
            editor_engine.draw_editor_grid(canvas, canvas.winfo_width(), canvas.winfo_height(), 10, state["pan_x"], state["pan_y"])
            
            # Принудительно обновляем плашку зума, если сохранен обратный вызов
            if hasattr(canvas, "trigger_mouse_zoom_callback"):
                canvas.trigger_mouse_zoom_callback("")
        except Exception: pass
    def action_save_project_as():
        """Принудительное сохранение проекта ЧПУ в новый файл .cam с выбором имени"""
        f_path = filedialog.asksaveasfilename(defaultextension=".cam", filetypes=[("Проект ЧПУ", "*.cam")])
        if not f_path: return
        
        # Готовим монолитную структуру данных JSON
        project_data = {
            "project_meta": {
                "pan_x": state["pan_x"],
                "pan_y": state["pan_y"],
                "scale": state["scale"]
            },
            "cnc_settings": editor_engine.CNC_SETTINGS,
            "geometry": editor_engine.DRAWN_ELEMENTS
        }
        try:
            with open(f_path, "w", encoding="utf-8") as f:
                json.dump(project_data, f, ensure_ascii=False, indent=2)
            state["project_path"] = f_path # Запоминаем путь
        except Exception: pass

    def action_save_project():
        """Быстрое сохранение изменений. Если файл новый — перенаправляет на 'Сохранить как'"""
        if state["project_path"]:
            project_data = {
                "project_meta": {
                    "pan_x": state["pan_x"],
                    "pan_y": state["pan_y"],
                    "scale": state["scale"]
                },
                "cnc_settings": editor_engine.CNC_SETTINGS,
                "geometry": editor_engine.DRAWN_ELEMENTS
            }
            try:
                with open(state["project_path"], "w", encoding="utf-8") as f:
                    json.dump(project_data, f, ensure_ascii=False, indent=2)
            except Exception: pass
        else:
            action_save_project_as()

    # --- ВОЗВРАЩАЕМ И УПАКОВЫВАЕМ ВСЕ 4 КНОПКИ БЛОКА 1 НА ЭКРАН ---
    btn_new = create_toolbar_button(files_group, "new.png", "Новый", action_new_project)
    btn_new.pack(side=tk.LEFT, padx=1)

    btn_open = create_toolbar_button(files_group, "open.png", "Открыть", action_open_project)
    btn_open.pack(side=tk.LEFT, padx=1)

    btn_save = create_toolbar_button(files_group, "save.png", "Сохранить", action_save_project)
    btn_save.pack(side=tk.LEFT, padx=1)

    btn_save_as = create_toolbar_button(files_group, "save_as.png", "Сохранить как", action_save_project_as)
    btn_save_as.pack(side=tk.LEFT, padx=1)

    # --- СЕКЦИЯ 2: ГРАВИРОВКА ТЕКСТА (БЛОК 2) ---
    sep1 = ttk.Separator(toolbar, orient="vertical")
    sep1.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=4)

    text_group = tk.Frame(toolbar, bg="#eaeaea")
    text_group.pack(side=tk.LEFT, padx=2, pady=2)

    # Поле ввода 'Текст:' вырезано. Оставляем только настройки стиля:
    combo_font = ttk.Combobox(text_group, values=["Arial", "Times New Roman", "Impact"], state="readonly", width=10)
    combo_font.current(0)
    combo_font.pack(side=tk.LEFT, padx=2)

    ent_font_size = ttk.Entry(text_group, width=4)
    ent_font_size.insert(0, "30")
    ent_font_size.pack(side=tk.LEFT, padx=2)

    # Сохраняем ссылки в объекте canvas, чтобы модуль мыши знал, какой шрифт применить в рамке
    canvas.text_entry_widgets = (combo_font, ent_font_size)

    btn_text_mode = create_toolbar_button(text_group, "text.png", "Текст 🔤", lambda: state["active_tool"].set("text"))
    btn_text_mode.pack(side=tk.LEFT, padx=2)

    # --- БЛОК 3 И БЛОК 4: ИНСТРУМЕНТЫ ГЕОМЕТРИИ И МЫШИ ---
    sep2 = ttk.Separator(toolbar, orient="vertical")
    sep2.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=4)

    geom_group = tk.Frame(toolbar, bg="#eaeaea")
    geom_group.pack(side=tk.LEFT, padx=2, pady=2)

    def set_tool(tool_name, btn_widget):
        state["active_tool"].set(tool_name)
        for b in tool_buttons.values(): 
            b.config(bg="#ffffff", fg="black", font=("Arial", 9))
        btn_widget.config(bg="#4a90e2", fg="white", font=("Arial", 9, "bold"))

    tool_buttons = {}
    tools_config = [
        ("Линия 🪵", "line.png", "Линия", "line"), 
        ("Прямоугольник 🟦", "rect.png", "Прямоугольник", "rect"), 
        ("Окружность ⭕", "oval.png", "Окружность", "oval"), 
        ("Панорама 🖐️", "pan.png", "Панорама", "pan"),
        ("Выделение 🎯", "select.png", "Выделение", "move_item")
    ]
    
    for t_lbl, t_icon, def_txt, t_name in tools_config:
        btn = create_toolbar_button(geom_group, t_icon, t_lbl)
        btn.config(command=lambda b=btn, t=t_name: set_tool(t, b))
        btn.pack(side=tk.LEFT, padx=1)
        tool_buttons[t_name] = btn

    # Переносим ссылку на кнопки в холст, чтобы модуль мыши мог сбрасывать стили при авто-переключении режимов
    canvas.toolbar_buttons_cache = tool_buttons
    tool_buttons["move_item"].config(bg="#4a90e2", fg="white", font=("Arial", 9, "bold"))

    # --- БЛОК 5: ПАРАМЕТРЫ ФРЕЗЕРОВАНИЯ ЧПУ ---
    sep3 = ttk.Separator(toolbar, orient="vertical")
    sep3.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=4)

    cnc_group = tk.Frame(toolbar, bg="#eaeaea")
    cnc_group.pack(side=tk.LEFT, padx=2, pady=2)

    def open_cnc_settings_window():
        win = tk.Toplevel(canvas)
        win.title(" Настройки режимов ЧПУ ")
        win.geometry("310x240")
        win.resizable(False, False)
        win.grab_set()
        win.geometry(f"+{canvas.winfo_rootx() + 50}+{canvas.winfo_rooty() + 50}")

        labels = [
            ("Безопасная высота Z (мм):", "z_safe"),
            ("Плоскость отвода Z (мм):", "z_clear"),
            ("Рабочая подача F (мм/мин):", "feed_xy"),
            ("Подача врезания Fz (мм/мин):", "feed_z"),
            ("Обороты шпинделя S (об/мин):", "spindle_s")
        ]
        entries_win = {}
        for idx, (lbl_txt, key) in enumerate(labels):
            ttk.Label(win, text=lbl_txt).grid(row=idx, column=0, sticky=tk.W, padx=15, pady=4)
            ent = ttk.Entry(win, width=10)
            ent.insert(0, editor_engine.CNC_SETTINGS[key])
            ent.grid(row=idx, column=1, padx=15, pady=4, sticky=tk.W)
            entries_win[key] = ent
            
        def save_and_close():
            editor_engine.update_cnc_settings(
                entries_win["z_safe"].get(), entries_win["z_clear"].get(),
                entries_win["feed_xy"].get(), entries_win["feed_z"].get(),
                entries_win["spindle_s"].get()
            )
            win.destroy()

        btn_save = tk.Button(win, text="СОХРАНИТЬ REЖИМЫ", bg="#1d4182", fg="white", font=("Arial", 9, "bold"), bd=0, height=2, command=save_and_close)
        btn_save.grid(row=5, column=0, columnspan=2, sticky="ew", padx=15, pady=15)

    btn_cnc = create_toolbar_button(cnc_group, "cnc.png", "⚙️ Режимы ЧПУ", open_cnc_settings_window)
    btn_cnc.pack(side=tk.LEFT, padx=1)
    
    btn_cnc_stub = create_toolbar_button(cnc_group, "stub_curve.png", "📄~")
    btn_cnc_stub.pack(side=tk.LEFT, padx=1)

    # --- БЛОК 6: ВНУТРЕННИЙ БУФЕР ОБМЕНА СИСТЕМЫ ---
    sep4 = ttk.Separator(toolbar, orient="vertical")
    sep4.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=4)

    clipboard_group = tk.Frame(toolbar, bg="#eaeaea")
    clipboard_group.pack(side=tk.LEFT, padx=2, pady=2)

    def action_copy():
        global EDITOR_CLIPBOARD
        if state["selected_id"]:
            for elem in editor_engine.DRAWN_ELEMENTS:
                if elem.get("id") == state["selected_id"]:
                    EDITOR_CLIPBOARD = copy.deepcopy(elem)
                    break

    def action_cut():
        global EDITOR_CLIPBOARD
        if state["selected_id"]:
            action_copy()
            canvas.delete(state["selected_id"])
            editor_engine.DRAWN_ELEMENTS = [e for e in editor_engine.DRAWN_ELEMENTS if e.get("id") != state["selected_id"]]
            state["selected_id"] = None

    def action_paste():
        global EDITOR_CLIPBOARD
        if EDITOR_CLIPBOARD:
            new_elem = copy.deepcopy(EDITOR_CLIPBOARD)
            new_elem["id"] = None
            if "coords" in new_elem:
                new_elem["coords"] = [c + 30 for c in new_elem["coords"]]
            
            if new_elem["type"] == "line":
                new_id = canvas.create_line(*new_elem["coords"], fill="#1d4182", width=2, tags="drawn_line")
                new_elem["id"] = new_id
            elif new_elem["type"] == "rect":
                new_id = canvas.create_rectangle(*new_elem["coords"], outline="#1d4182", width=2, tags="drawn_line")
                new_elem["id"] = new_id
            elif new_elem["type"] == "oval":
                new_id = canvas.create_oval(*new_elem["coords"], outline="#1d4182", width=2, tags="drawn_line")
                new_elem["id"] = new_id
                
            if new_elem["id"]:
                editor_engine.DRAWN_ELEMENTS.append(new_elem)

    # Сохраняем ссылки на команды буфера для контекстного меню ПКМ
    canvas.clipboard_commands_cache = (action_copy, action_cut, action_paste)

    btn_paste = create_toolbar_button(clipboard_group, "paste.png", "Вставить", action_paste)
    btn_paste.pack(side=tk.LEFT, padx=1)

    btn_copy = create_toolbar_button(clipboard_group, "copy.png", "Копировать", action_copy)
    btn_copy.pack(side=tk.LEFT, padx=1)

    btn_cut = create_toolbar_button(clipboard_group, "cut.png", "Вырезать", action_cut)
    btn_cut.pack(side=tk.LEFT, padx=1)

    # --- БЛОК 7: ИМПОРТ И ПРОМЫШЛЕННЫЙ CAM-ЭКСПОРТ G-КОДА ---
    sep5 = ttk.Separator(toolbar, orient="vertical")
    sep5.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=4)

    io_group = tk.Frame(toolbar, bg="#eaeaea")
    io_group.pack(side=tk.LEFT, padx=2, pady=2)

    def trigger_dxf_import():
        f_path = filedialog.askopenfilename(filetypes=[("AutoCAD Чертеж", "*.dxf"), ("Все файлы", "*.*")])
        if f_path:
            editor_engine.import_dxf_file_engine(canvas, f_path, state["pan_x"], state["pan_y"])

    def trigger_tap_export():
        f_path = filedialog.asksaveasfilename(defaultextension=".tap", filetypes=[("ЧПУ Программа", "*.tap")])
        if not f_path: return
        try:
            with open(f_path, "w", encoding="utf-8") as f:
                f.write(f"% \nG21 (ММ)\nG90 (АБСОЛЮТНЫЕ КООРДИНАТЫ)\nG00 Z{editor_engine.CNC_SETTINGS['z_safe']}\n")
                f.write(f"M03 S{editor_engine.CNC_SETTINGS['spindle_s']}\n")
                
                for elem in editor_engine.DRAWN_ELEMENTS:
                    if "coords" in elem and len(elem["coords"]) >= 4:
                        x1, y1, x2, y2 = elem["coords"]
                        f.write(f"G00 X{x1:.3f} Y{y1:.3f}\n") 
                        f.write(f"G01 Z-2.000 F{editor_engine.CNC_SETTINGS['feed_z']}\n") 
                        f.write(f"G01 X{x2:.3f} Y{y2:.3f} F{editor_engine.CNC_SETTINGS['feed_xy']}\n") 
                        f.write(f"G00 Z{editor_engine.CNC_SETTINGS['z_safe']}\n") 
                        
                f.write("M05 (СТОП ШПИНДЕЛЬ)\nG00 X0 Y0\nM30\n%\n")
        except Exception: 
            pass

    btn_exp_dxf = create_toolbar_button(io_group, "exp_dxf.png", "Экспорт DXF")
    btn_exp_dxf.pack(side=tk.LEFT, padx=1)

    btn_exp_tap = create_toolbar_button(io_group, "exp_tap.png", "Экспорт TAP", trigger_tap_export)
    btn_exp_tap.pack(side=tk.LEFT, padx=1)

    btn_imp_dxf = create_toolbar_button(io_group, "imp_dxf.png", "Импорт DXF", trigger_dxf_import)
    btn_imp_dxf.pack(side=tk.LEFT, padx=1)
