import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from modules import editor_engine

def load_editor_interface(params_frame, canvas, controller):
    """
    Графический интерфейс CAM-редактора ЧПУ стола.
    Полный набор кнопок: Линии, Фигуры, Панорама, Перетаскивание деталей,
    Гравировка текста, Магнитная привязка и Менеджер настроек ЧПУ.
    """
    # Очищаем холст от старых кнопок изделий
    for widget in canvas.winfo_children(): 
        widget.destroy()
    canvas.delete("all")
    
    w_width = canvas.winfo_width() if canvas.winfo_width() > 100 else 800
    w_height = canvas.winfo_height() if canvas.winfo_height() > 100 else 450

    # Смещение панорамы координатного стола
    pan_offset_x = 0
    pan_offset_y = 0

    # Чертим стартовую сетку ЧПУ стола
    editor_engine.draw_editor_grid(canvas, w_width, w_height, 10, pan_offset_x, pan_offset_y)

    # --- ПАНЕЛЬ 1: МАСШТАБИРОВАНИЕ ЧЕРТЕЖА ---
    scale_frame = ttk.LabelFrame(params_frame, text=" Масштабирование чертежа ", padding=10)
    scale_frame.pack(fill=tk.X, padx=10, pady=5)

    ttk.Label(scale_frame, text="Масштаб (%):").grid(row=0, column=0, sticky=tk.W, pady=3)
    ent_scale = ttk.Entry(scale_frame, width=8)
    ent_scale.insert(0, "100")
    ent_scale.grid(row=0, column=1, padx=5, pady=3, sticky=tk.W)

    ttk.Label(scale_frame, text="Ширина X (мм):").grid(row=1, column=0, sticky=tk.W, pady=3)
    ent_width = ttk.Entry(scale_frame, width=8)
    ent_width.insert(0, "0")
    ent_width.grid(row=1, column=1, padx=5, pady=3, sticky=tk.W)

    def execute_scale_action():
        """Считывает значения из полей ввода и запускает масштабирование"""
        try:
            pct_val = float(ent_scale.get()) if ent_scale.get() else 100.0
            mm_width = float(ent_width.get()) if ent_width.get() else 0.0
            
            if mm_width > 0:
                editor_engine.scale_all_drawn_elements_engine(canvas, target_w=mm_width)
            else:
                editor_engine.scale_all_drawn_elements_engine(canvas, scale_pct=pct_val)
        except ValueError:
            pass

    btn_apply_scale = tk.Button(scale_frame, text="ПРИМЕНИТЬ МАСШТАБ", bg="#1d4182", fg="white", font=("Arial", 9, "bold"), bd=0, height=2, command=execute_scale_action)
    btn_apply_scale.grid(row=2, column=0, columnspan=2, sticky="ew", pady=8)

    # --- ПАНЕЛЬ 2: РЕЖИМЫ РИСОВАНИЯ И ПЕРЕМЕЩЕНИЯ ---
    tool_frame = ttk.LabelFrame(params_frame, text=" Инструменты ЧПУ ", padding=8)
    tool_frame.pack(fill=tk.X, padx=10, pady=4)

    # Переменная текущего активного инструмента
    active_tool = tk.StringVar(value="line")

    def set_tool(tool_name, btn_widget):
        active_tool.set(tool_name)
        for b in tool_buttons.values(): 
            b.config(bg="#eaeaea", fg="black", font=("Arial", 9))
        btn_widget.config(bg="#4a90e2", fg="white", font=("Arial", 9, "bold"))

    tool_buttons = {}
    tools_config = [
        ("Линия", "line"), 
        ("Прямоугольник", "rect"), 
        ("Окружность", "oval"), 
        ("Панорама стола 🖐️", "pan"),
        ("Перетащить фигуру 🎯", "move_item")
    ]
    
    for t_lbl, t_name in tools_config:
        btn = tk.Button(tool_frame, text=t_lbl, bg="#eaeaea", fg="black", bd=1, relief=tk.GROOVE, height=1, anchor=tk.CENTER)
        btn.config(command=lambda b=btn, t=t_name: set_tool(t, b))
        btn.pack(fill=tk.X, pady=2)
        tool_buttons[t_name] = btn
    
    # По умолчанию активна обычная линия
    tool_buttons["line"].config(bg="#4a90e2", fg="white", font=("Arial", 9, "bold"))

    # --- ПАНЕЛЬ 3: ИМПОРТ, НАСТРОЙКИ И ИСТОРИЯ ---
    io_frame = ttk.LabelFrame(params_frame, text=" Операции УП ", padding=8)
    io_frame.pack(fill=tk.X, padx=10, pady=4)

    def trigger_dxf_import():
        f_path = filedialog.askopenfilename(filetypes=[("AutoCAD Чертеж", "*.dxf"), ("Все файлы", "*.*")])
        if f_path:
            editor_engine.import_dxf_file_engine(canvas, f_path, pan_offset_x, pan_offset_y)

    btn_dxf = tk.Button(io_frame, text="Импорт DXF (AutoCAD)", bg="#eaeaea", fg="#1d4182", font=("Arial", 9, "bold"), bd=1, relief=tk.GROOVE)
    btn_dxf.config(command=trigger_dxf_import)
    btn_dxf.pack(fill=tk.X, pady=2)

    # Окно глобальных настроек ЧПУ со скоростями и безопасной высотой Z
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

        btn_save = tk.Button(win, text="СОХРАНИТЬ РЕЖИМЫ", bg="#4a90e2", fg="white", font=("Arial", 9, "bold"), bd=0, height=2, command=save_and_close)
        btn_save.grid(row=5, column=0, columnspan=2, sticky="ew", padx=15, pady=15)

    btn_settings = tk.Button(io_frame, text="⚙️ Параметры режимов ЧПУ", bg="#eaeaea", fg="#444444", font=("Arial", 9), bd=1, relief=tk.GROOVE)
    btn_settings.config(command=open_cnc_settings_window)
    btn_settings.pack(fill=tk.X, pady=2)

    hist_frame = ttk.Frame(io_frame)
    hist_frame.pack(fill=tk.X, pady=4)

    def history_action(action_type):
        if action_type == "clear":
            canvas.delete("drawn_line", "vector_text", "dxf_group")
            editor_engine.DRAWN_ELEMENTS = []
            editor_engine.HISTORY_REDO = []

    btn_undo = tk.Button(hist_frame, text=" ◀ ", width=4, bg="#eaeaea", command=lambda: history_action("undo"))
    btn_clear = tk.Button(hist_frame, text=" Сброс ", bg="#eaeaea", command=lambda: history_action("clear"))
    btn_redo = tk.Button(hist_frame, text=" ▶ ", width=4, bg="#eaeaea", command=lambda: history_action("redo"))
    
    btn_undo.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
    btn_clear.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
    btn_redo.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

    # --- ПАНЕЛЬ 4: ГРАВИРОВКА ТЕКСТА ---
    text_frame = ttk.LabelFrame(params_frame, text=" Гравировка текста ЧПУ ", padding=8)
    text_frame.pack(fill=tk.X, padx=10, pady=4)

    ent_msg = ttk.Entry(text_frame, width=15); ent_msg.insert(0, "Банька"); ent_msg.pack(fill=tk.X, pady=2)
    combo_font = ttk.Combobox(text_frame, values=["Arial", "Times New Roman", "Courier", "Impact"], state="readonly")
    combo_font.current(0); combo_font.pack(fill=tk.X, pady=2)
    ent_font_size = ttk.Entry(text_frame, width=8); ent_font_size.insert(0, "30"); ent_font_size.pack(fill=tk.X, pady=2)

    btn_text_mode = tk.Button(text_frame, text="Поставить текст", bg="#eaeaea", command=lambda: active_tool.set("text"))
    btn_text_mode.pack(fill=tk.X, pady=3)



    # --- ЛОГИКА МЫШКИ (РИСОВАНИЕ, ПАНОРАМА, ПЕРЕТАСКИВАНИЕ И МАГНИТ 🧲) ---
    start_x, start_y = None, None
    temp_item = None        
    dragged_item = None     
    snap_marker = None      # Зеленый крестик магнитной привязки

    def update_snap_visualization(event):
        """Отслеживает движение мыши и подсвечивает точки прилипания"""
        nonlocal snap_marker
        if snap_marker: 
            canvas.delete(snap_marker)
            snap_marker = None
            
        tool = active_tool.get()
        # Магнит работает только во время рисования фигур
        if tool in ["line", "rect", "oval"]:
            is_snapped, snap_x, snap_y = editor_engine.find_nearest_snap_point(canvas, event.x, event.y, snap_radius=15)
            if is_snapped:
                # Чертим технологический крестик привязки зелёного цвета
                r = 6
                l1 = canvas.create_line(snap_x - r, snap_y, snap_x + r, snap_y, fill="#28a745", width=2)
                l2 = canvas.create_line(snap_x, snap_y - r, snap_x, snap_y + r, fill="#28a745", width=2)
                snap_marker = canvas.create_rectangle(snap_x - 3, snap_y - 3, snap_x + 3, snap_y + 3, outline="#28a745", width=1)
                return True, snap_x, snap_y
        return False, event.x, event.y

    def on_click(event):
        nonlocal start_x, start_y, dragged_item
        
        # Проверяем привязку перед фиксацией первой точки клика
        is_snapped, use_x, os_y = update_snap_visualization(event)
        start_x = use_x if is_snapped else event.x
        start_y = os_y if is_snapped else event.y
        
        tool = active_tool.get()
        
        if tool == "move_item":
            closest = canvas.find_closest(event.x, event.y, halo=15)
            if closest:
                item_id = closest
                tags = canvas.gettags(item_id)
                if "grid_line" not in tags:
                    dragged_item = item_id
                    canvas.itemconfig(dragged_item, width=3)
        
        elif tool == "text":
            editor_engine.place_vector_text_on_table(canvas, ent_msg.get(), event.x, event.y, combo_font.get(), ent_font_size.get())
            active_tool.set("line") 
            for b in tool_buttons.values(): 
                b.config(bg="#eaeaea", fg="black", font=("Arial", 9))
            tool_buttons["line"].config(bg="#4a90e2", fg="white", font=("Arial", 9, "bold"))

    def on_drag(event):
        nonlocal start_x, start_y, temp_item, pan_offset_x, pan_offset_y, dragged_item
        if start_x is None or start_y is None: return
        
        tool = active_tool.get()
        
        # Проверяем привязку для конечной точки во время ведения фигуры
        is_snapped, use_x, os_y = update_snap_visualization(event)
        current_target_x = use_x if is_snapped else event.x
        current_target_y = os_y if is_snapped else event.y
        
        if tool == "line":
            canvas.create_line(start_x, start_y, current_target_x, current_target_y, fill="#1d4182", width=2, tags="drawn_line")
            start_x = current_target_x
            start_y = current_target_y
            
        elif tool == "rect":
            if temp_item: canvas.delete(temp_item)
            temp_item = canvas.create_rectangle(start_x, start_y, current_target_x, current_target_y, outline="#1d4182", width=2, tags="drawn_line")
            
        elif tool == "oval":
            if temp_item: canvas.delete(temp_item)
            temp_item = canvas.create_oval(start_x, start_y, current_target_x, current_target_y, outline="#1d4182", width=2, tags="drawn_line")
            
        elif tool == "pan":
            dx = event.x - start_x
            dy = event.y - start_y
            pan_offset_x += dx
            pan_offset_y += dy
            canvas.move("drawn_line", dx, dy)
            canvas.move("vector_text", dx, dy)
            canvas.move("dxf_group", dx, dy)
            editor_engine.draw_editor_grid(canvas, canvas.winfo_width(), canvas.winfo_height(), 10, pan_offset_x, pan_offset_y)
            start_x = event.x
            start_y = event.y
            
        elif tool == "move_item" and dragged_item is not None:
            dx = event.x - start_x
            dy = event.y - start_y
            tags = canvas.gettags(dragged_item)
            if "dxf_group" in tags:
                canvas.move("dxf_group", dx, dy)
            else:
                canvas.move(dragged_item, dx, dy)
            start_x = event.x
            start_y = event.y

    def on_release(event):
        nonlocal temp_item, dragged_item, snap_marker
        if dragged_item is not None:
            tags = canvas.gettags(dragged_item)
            if "dxf_group" not in tags:
                canvas.itemconfig(dragged_item, width=2)
            dragged_item = None
        temp_item = None 
        if snap_marker:
            canvas.delete(snap_marker)
            snap_marker = None

    # Привязываем события мыши к холсту
    canvas.bind("<Motion>", update_snap_visualization)
    canvas.bind("<Button-1>", on_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    # --- КОНТЕКСТНОЕ МЕНЮ ПКМ ---
    ctx_menu = tk.Menu(canvas, tearoff=0, font=("Arial", 10), bg="#ffffff", fg="#333333", activebackground="#4a90e2")
    lock_var = tk.IntVar(value=0)

    def show_context_menu(event):
        ctx_menu.delete(0, tk.END)
        mm_x = int(event.x - pan_offset_x)
        mm_y = int(event.y - pan_offset_y)

        ctx_menu.add_command(label=f" Координаты ЧПУ: X={mm_x}мм, Y={mm_y}мм ", state="disabled")
        ctx_menu.add_separator()
        ctx_menu.add_checkbutton(label=" Зафиксировать положение (Замок 🔒)", variable=lock_var)
        ctx_menu.add_separator()
        ctx_menu.add_command(label=" Сместить весь чертеж DXF ", state="disabled")
        ctx_menu.post(event.x_root, event.y_root)

    canvas.bind("<Button-3>", show_context_menu)
