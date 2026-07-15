import tkinter as tk
from tkinter import ttk
from modules import cam_drawer  # Подключаем наш универсальный графический движок

def load_pipe_interface(params_frame, canvas, controller):
    """
    Интерфейс 'Пазировка бани' (набор досок для бани-бочки).
    """
    # Очищаем холст от старых кнопок принудительно при входе в модуль
    for widget in canvas.winfo_children():
        widget.destroy()

    canvas_container = tk.Canvas(params_frame, borderwidth=0, highlightthickness=0)
    scrollbar = ttk.Scrollbar(params_frame, orient="vertical", command=canvas_container.yview)
    scrollable_frame = ttk.Frame(canvas_container)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas_container.configure(scrollregion=canvas_container.bbox("all"))
    )
    canvas_container.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas_container.configure(yscrollcommand=scrollbar.set)
    canvas_container.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    mode_var = tk.StringVar(value="Верх") 
    entries = {}
    room_vars = {} 

    def toggle_lock(entry_widget, var):
        if var.get() == 1:
            entry_widget.config(state="normal")
        else:
            entry_widget.config(state="disabled")
        update_preview(canvas, entries, mode_var, room_vars)

    # --- 1. КНОПКИ РЕЖИМА ОБРАБОТКИ ---
    mode_frame = ttk.Frame(scrollable_frame, padding=2)
    mode_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=5, padx=5)
    
    btn_top = tk.Button(mode_frame, text="Верх трубы", font=("Arial", 9, "bold"), bg="#4a90e2", fg="white", bd=1, relief=tk.RAISED, width=12)
    btn_bottom = tk.Button(mode_frame, text="Низ трубы", font=("Arial", 9), bg="#eaeaea", fg="black", bd=1, relief=tk.FLAT, width=12)
    
    btn_top.pack(side=tk.LEFT, padx=2)
    btn_bottom.pack(side=tk.LEFT, padx=2)

    # --- 2. ПОЛЯ ВВОДА ---
    ttk.Label(scrollable_frame, text="Диаметр фрезы (мм):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
    entry_cutter = ttk.Entry(scrollable_frame, width=8)
    entry_cutter.insert(0, "11.2")
    entry_cutter.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
    entries["cutter_dia"] = entry_cutter

    ttk.Label(scrollable_frame, text="Ширина паза (мм):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
    entry_slot = ttk.Entry(scrollable_frame, width=8, state="disabled")
    entry_slot.config(state="normal")
    entry_slot.insert(0, "45.0")
    entry_slot.config(state="disabled")
    entry_slot.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
    entries["slot_width"] = entry_slot
    chk_slot_var = tk.IntVar(value=0)
    chk_slot = ttk.Checkbutton(scrollable_frame, variable=chk_slot_var, command=lambda: toggle_lock(entry_slot, chk_slot_var))
    chk_slot.grid(row=2, column=2, padx=2, sticky=tk.W)

    ttk.Label(scrollable_frame, text="Глубина пазов Z (мм):").grid(row=3, column=0, sticky=tk.W, pady=2)
    entry_z_slots = ttk.Entry(scrollable_frame, width=8, state="disabled")
    entry_z_slots.config(state="normal")
    entry_z_slots.insert(0, "-20.0")
    entry_z_slots.config(state="disabled")
    entry_z_slots.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
    entries["z_slots"] = entry_z_slots
    chk_z_var = tk.IntVar(value=0)
    chk_z = ttk.Checkbutton(scrollable_frame, variable=chk_z_var, command=lambda: toggle_lock(entry_z_slots, chk_z_var))
    chk_z.grid(row=3, column=2, padx=2, sticky=tk.W)

    ttk.Label(scrollable_frame, text="Глубина торцевания Z (мм):").grid(row=4, column=0, sticky=tk.W, pady=2)
    entry_z_trim = ttk.Entry(scrollable_frame, width=8)
    entry_z_trim.insert(0, "-46.0")
    entry_z_trim.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
    entries["z_trim"] = entry_z_trim

    ttk.Label(scrollable_frame, text="Рабочая подача F (мм/мин):").grid(row=5, column=0, sticky=tk.W, pady=2)
    entry_feed = ttk.Entry(scrollable_frame, width=8, state="disabled")
    entry_feed.config(state="normal")
    entry_feed.insert(0, "2000")
    entry_feed.config(state="disabled")
    entry_feed.grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)
    entries["feed_rate"] = entry_feed

    ttk.Label(scrollable_frame, text="Ширина лежки X (мм):").grid(row=6, column=0, sticky=tk.W, pady=2)
    entry_wood_x = ttk.Entry(scrollable_frame, width=8)
    entry_wood_x.insert(0, "1400.0")
    entry_wood_x.grid(row=6, column=1, sticky=tk.W, padx=5, pady=2)
    entries["wood_width_x"] = entry_wood_x

    ttk.Label(scrollable_frame, text="Передний выпуск (мм):").grid(row=7, column=0, sticky=tk.W, padx=5, pady=2)
    entry_front = ttk.Entry(scrollable_frame, width=8, state="disabled")
    entry_front.config(state="normal")
    entry_front.insert(0, "50.0")
    entry_front.config(state="disabled")
    entry_front.grid(row=7, column=1, sticky=tk.W, padx=5, pady=2)
    entries["front_offset"] = entry_front
    chk_front_var = tk.IntVar(value=0)
    chk_front = ttk.Checkbutton(scrollable_frame, variable=chk_front_var, command=lambda: toggle_lock(entry_front, chk_front_var))
    chk_front.grid(row=7, column=2, padx=2, sticky=tk.W)

    # --- 3. ДИНАМИЧЕСКИЙ ЗАДНИЙ ВЫПУСК ---
    lbl_back_release = ttk.Label(scrollable_frame, text="Задний выпуск (мм):")
    lbl_back_release.grid(row=8, column=0, sticky=tk.W, padx=5, pady=2)
    entry_back = ttk.Entry(scrollable_frame, width=8)
    entry_back.insert(0, "50.0")
    entry_back.grid(row=8, column=1, sticky=tk.W, padx=5, pady=2)
    entries["back_offset"] = entry_back

    def set_mode(selected_mode):
        mode_var.set(selected_mode)
        if selected_mode == "Верх":
            btn_top.config(bg="#4a90e2", fg="white", relief=tk.RAISED)
            btn_bottom.config(bg="#eaeaea", fg="black", relief=tk.FLAT)
        else:
            btn_top.config(bg="#eaeaea", fg="black", relief=tk.FLAT)
            btn_bottom.config(bg="#4a90e2", fg="white", relief=tk.RAISED)
        update_preview(canvas, entries, mode_var, room_vars)

    btn_top.config(command=lambda: set_mode("Верх"))
    btn_bottom.config(command=lambda: set_mode("Низ"))

    # --- 4. БЛОК КОМНАТ ---
    room_start_row = 9
    for i in range(1, 6):
        row_idx = room_start_row + i - 1
        ttk.Label(scrollable_frame, text=f"Длина комнаты {i} (мм):").grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)
        
        is_first = (i == 1)
        init_state = "normal" if is_first else "disabled"
        init_val = "2000.0" if is_first else "0.0"
        if i == 2: init_val = "1765.0"
        
        ent_room = ttk.Entry(scrollable_frame, width=8, state=init_state)
        if not is_first:
            box_state = "normal" if (i == 2) else "disabled"
            ent_room.config(state="normal")
            ent_room.insert(0, init_val)
            ent_room.config(state=box_state)
        else:
            ent_room.insert(0, init_val)
            
        ent_room.grid(row=row_idx, column=1, sticky=tk.W, padx=5, pady=2)
        entries[f"room_{i}"] = ent_room
        
        chk_var = tk.IntVar(value=1 if (i <= 2) else 0)
        room_vars[f"room_{i}"] = chk_var
        
        chk_cmd = lambda e=ent_room, v=chk_var: toggle_lock(e, v)
        chk_room = ttk.Checkbutton(scrollable_frame, variable=chk_var, command=chk_cmd)
        chk_room.grid(row=row_idx, column=2, padx=2, sticky=tk.W)

    for entry in entries.values():
        entry.bind("<KeyRelease>", lambda e: update_preview(canvas, entries, mode_var, room_vars))

    # Кнопка «Обновить»
    btn_refresh = tk.Button(
        canvas, text="Обновить", bg="#eaeaea", fg="#333333", activebackground="#d5d5d5",
        font=("Arial", 9), bd=1, relief=tk.GROOVE, width=10,
        command=lambda: update_preview(canvas, entries, mode_var, room_vars)
    )
    btn_refresh.pack(side=tk.TOP, anchor=tk.NE, padx=15, pady=15)

    controller.active_inputs = entries
    controller.active_inputs["mode_var"] = mode_var
    controller.active_inputs["room_vars"] = room_vars

    canvas.bind("<Configure>", lambda e: update_preview(canvas, entries, mode_var, room_vars))
    update_preview(canvas, entries, mode_var, room_vars)


def update_preview(canvas, entries, mode_var, room_vars):
    """Пазировка Бани: передает параметры в центральный движок cam_drawer"""
    try:
        if not entries or "slot_width" not in entries: return
        slot_w = float(entries["slot_width"].get()) if entries["slot_width"].get() else 45.0
        front_v = float(entries["front_offset"].get()) if entries["front_offset"].get() else 50.0
        back_v = float(entries["back_offset"].get()) if entries["back_offset"].get() else 50.0
        wood_x = float(entries["wood_width_x"].get()) if entries["wood_width_x"].get() else 1400.0
        
        active_rooms = []
        for i in range(1, 6):
            if room_vars[f"room_{i}"].get() == 1:
                r_text = entries[f"room_{i}"].get()
                active_rooms.append(float(r_text) if r_text else 0.0)
    except (ValueError, KeyError, TypeError):
        return

    total_slots = len(active_rooms) + 1 if active_rooms else 0
    cam_drawer.draw_paz_beam_engine(canvas, front_v, back_v, wood_x, slot_w, active_rooms, mode_var.get(), total_slots)


def load_custom_paz_interface(params_frame, canvas, controller):
    """Произвольная пазировка с динамическим скроллингом и чистыми нулями."""
    canvas.delete("all")
    canvas_container = tk.Canvas(params_frame, borderwidth=0, highlightthickness=0, bg=params_frame.cget("bg"))
    scrollbar = ttk.Scrollbar(params_frame, orient="vertical", command=canvas_container.yview)
    scroll_frame = ttk.Frame(canvas_container)

    def update_scroll_region(event=None):
        canvas_container.configure(scrollregion=canvas_container.bbox("all"))

    scroll_frame.bind("<Configure>", update_scroll_region)
    canvas_container.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas_container.pack(side="left", fill="both", expand=True)
    scroll_window = canvas_container.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas_container.bind("<Configure>", lambda e: canvas_container.itemconfig(scroll_window, width=e.width))

    def _on_mousewheel(event):
        canvas_container.yview_scroll(int(-1*(event.delta/120)), "units")
    scroll_frame.bind_all("<MouseWheel>", _on_mousewheel)

    controller.active_inputs = {"paz_blocks": {}, "torc_blocks": {}}

    def trigger_redraw(event=None):
        draw_custom_paz_preview(canvas, controller.active_inputs)

    # Базовые настройки
    base_frame = ttk.LabelFrame(scroll_frame, text=" Параметры: Произвольная пазировка ", padding=8)
    base_frame.pack(fill=tk.X, padx=5, pady=4)

    ttk.Label(base_frame, text="Диаметр фрезы (мм):").grid(row=0, column=0, sticky=tk.W, pady=2)
    ent_cutter = ttk.Entry(base_frame, width=8)
    ent_cutter.insert(0, "11.2")
    ent_cutter.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
    controller.active_inputs["cutter_dia"] = ent_cutter
    ent_cutter.bind("<KeyRelease>", trigger_redraw)

    ttk.Label(base_frame, text="Рабочая подача F (мм/мин):").grid(row=1, column=0, sticky=tk.W, pady=2)
    ent_feed = ttk.Entry(base_frame, width=8)
    ent_feed.insert(0, "2000")
    ent_feed.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
    controller.active_inputs["feed_rate"] = ent_feed
    ent_feed.bind("<KeyRelease>", trigger_redraw)

    # Пазы (10 блоков)
    paz_header_frame = ttk.LabelFrame(scroll_frame, text=" Параметры: Пазы ", padding=5)
    paz_header_frame.pack(fill=tk.X, padx=5, pady=6)

    def create_paz_block(parent, num):
        block_frame = ttk.Frame(parent)
        block_frame.pack(fill=tk.X, pady=2)
        chk_var = tk.IntVar(value=0)
        fields_frame = ttk.Frame(block_frame)

        def toggle_block():
            if chk_var.get() == 1: fields_frame.pack(fill=tk.X, padx=15, pady=2)
            else: fields_frame.pack_forget()
            canvas_container.after(10, update_scroll_region)
            trigger_redraw()

        chk_btn = ttk.Checkbutton(block_frame, text=f"Паз №{num}", variable=chk_var, command=toggle_block)
        chk_btn.pack(anchor=tk.NW, pady=2)

        labels = ["Ширина паза:", "Длинна паза:", "Глубина паза:", "Рассояние от 0 до паза:"]
        keys = ["width", "length", "depth", "offset"]
        block_entries = {"chk_var": chk_var}
        for idx, (lbl_text, key) in enumerate(zip(labels, keys)):
            ttk.Label(fields_frame, text=lbl_text).grid(row=idx, column=0, sticky=tk.W, pady=1)
            ent = ttk.Entry(fields_frame, width=8)
            ent.insert(0, "0")
            ent.grid(row=idx, column=1, padx=5, pady=1, sticky=tk.W)
            block_entries[key] = ent
            ent.bind("<KeyRelease>", trigger_redraw)
        controller.active_inputs["paz_blocks"][num] = block_entries

    for i in range(1, 11): create_paz_block(paz_header_frame, i)

    # Торцы (10 блоков)
    torc_header_frame = ttk.LabelFrame(scroll_frame, text=" Параметры: Торцы ", padding=5)
    torc_header_frame.pack(fill=tk.X, padx=5, pady=6)

    def create_torc_block(parent, num):
        block_frame = ttk.Frame(parent)
        block_frame.pack(fill=tk.X, pady=2)
        chk_var = tk.IntVar(value=0)
        fields_frame = ttk.Frame(block_frame)

        def toggle_block():
            if chk_var.get() == 1: fields_frame.pack(fill=tk.X, padx=15, pady=2)
            else: fields_frame.pack_forget()
            canvas_container.after(10, update_scroll_region)
            trigger_redraw()

        chk_btn = ttk.Checkbutton(block_frame, text=f"Торец №{num}", variable=chk_var, command=toggle_block)
        chk_btn.pack(anchor=tk.NW, pady=2)

        labels = ["Глубина торца:", "Длинна торца:", "Рассояние от 0 до торца:"]
        keys = ["depth", "length", "offset"]
        block_entries = {"chk_var": chk_var}
        for idx, (lbl_text, key) in enumerate(zip(labels, keys)):
            ttk.Label(fields_frame, text=lbl_text).grid(row=idx, column=0, sticky=tk.W, pady=1)
            ent = ttk.Entry(fields_frame, width=8)
            ent.insert(0, "0")
            ent.grid(row=idx, column=1, padx=5, pady=1, sticky=tk.W)
            block_entries[key] = ent
            ent.bind("<KeyRelease>", trigger_redraw)
        controller.active_inputs["torc_blocks"][num] = block_entries

    for i in range(1, 11): create_torc_block(torc_header_frame, i)
    canvas.bind("<Configure>", lambda e: trigger_redraw())
    trigger_redraw()

def draw_custom_paz_preview(canvas, active_inputs):
    """Произвольная пазировка: собирает только включенные блоки и шлет в свободный движок"""
    valid_pazes = []
    valid_torces = []
    has_active_elements = False

    # Считываем активные пазы
    for num, block in active_inputs["paz_blocks"].items():
        if block["chk_var"].get() == 1:
            has_active_elements = True
            try:
                w = float(block["width"].get()) if block["width"].get() else 0.0
                l = float(block["length"].get()) if block["length"].get() else 0.0
                d = float(block["depth"].get()) if block["depth"].get() else 0.0
                o = float(block["offset"].get()) if block["offset"].get() else 0.0
                if l > 0: valid_pazes.append({"num": num, "w": w, "l": l, "d": d, "o": o})
            except ValueError: pass

    # Считываем активные торцы
    for num, block in active_inputs["torc_blocks"].items():
        if block["chk_var"].get() == 1:
            has_active_elements = True
            try:
                d = float(block["depth"].get()) if block["depth"].get() else 0.0
                l = float(block["length"].get()) if block["length"].get() else 0.0
                o = float(block["offset"].get()) if block["offset"].get() else 0.0
                if l > 0: valid_torces.append({"num": num, "d": d, "l": l, "o": o})
            except ValueError: pass

    # Если всё выключено — чистим экран холста
    if not has_active_elements:
        canvas.delete("all")
        w_width, w_height = canvas.winfo_width(), canvas.winfo_height()
        if w_width < 100: w_width = 800
        if w_height < 100: w_height = 450
        canvas.create_text(w_width / 2, w_height / 2, 
                           text="[ Координатный стол пуст ]\nАктивируйте галочками нужные пазы или торцы слева", 
                           font=("Arial", 10, "italic"), fill="gray", justify=tk.CENTER)
        return

    # 🚀 ВЫЗЫВАЕМ НАШ СВЕЖИЙ, ЧЕСТНЫЙ ДВИЖОК ПРОИЗВОЛЬНЫХ КООРДИНАТ!
    cam_drawer.draw_custom_paz_engine(canvas, valid_pazes, valid_torces)


def load_plane_interface(params_frame, canvas, controller):
    """
    Генерирует интерфейс для третьей вкладки 'Выравнивание плоскости'.
    Параметры усечены до 8 символов в едином сером стиле ЧПУ компании.
    """
    canvas.delete("all")

    # Переменные состояния для стратегии обработки
    strategy_var = tk.StringVar(value="Зигзаг по Y") 
    entries = {}

    # --- 1. КНОПКИ ВЫБОРА ТРАЕКТОРИИ ---
    strat_frame = ttk.Frame(params_frame, padding=2)
    strat_frame.pack(anchor=tk.NW, fill=tk.X, padx=10, pady=5)
    
    btn_y = tk.Button(strat_frame, text="Зигзаг по Y", font=("Arial", 9, "bold"), bg="#4a90e2", fg="white", bd=1, relief=tk.RAISED, width=12)
    btn_x = tk.Button(strat_frame, text="Зигзаг по X", font=("Arial", 9), bg="#eaeaea", fg="black", bd=1, relief=tk.FLAT, width=12)
    
    btn_y.pack(side=tk.LEFT, padx=2)
    btn_x.pack(side=tk.LEFT, padx=2)

    # Контейнер полей ввода
    fields_frame = ttk.LabelFrame(params_frame, text=" Параметры плоскости стола ", padding=10)
    fields_frame.pack(fill=tk.X, padx=10, pady=5)

    # Список параметров согласно ТЗ
    plane_params = [
        ("Длина зоны Y (мм):", "size_y", "1000"),
        ("Ширина зоны X (мм):", "size_x", "600"),
        ("Диаметр фрезы (мм):", "tool_d", "35.0"),
        ("Перекрытие фрезы (%):", "overlap", "40"),
        ("Съем по оси Z (мм):", "z_deep", "-0.5"),
        ("Рабочая подача F (мм/мин):", "feed_f", "3000")
    ]

    def trigger_plane_redraw(event=None):
        """Пинает центральный графический модуль на прорисовку плоскости"""
        if "size_y" in entries:
            cam_drawer.draw_plane_alignment_engine(canvas, entries, strategy_var.get())

    for idx, (lbl_text, key_name, default_val) in enumerate(plane_params):
        ttk.Label(fields_frame, text=lbl_text).grid(row=idx, column=0, sticky=tk.W, pady=3)
        ent = ttk.Entry(fields_frame, width=8)
        ent.insert(0, default_val)
        ent.grid(row=idx, column=1, padx=5, pady=3, sticky=tk.W)
        entries[key_name] = ent
        ent.bind("<KeyRelease>", trigger_plane_redraw)

    def set_strategy(selected_strat):
        strategy_var.set(selected_strat)
        if selected_strat == "Зигзаг по Y":
            btn_y.config(bg="#4a90e2", fg="white", relief=tk.RAISED, font=("Arial", 9, "bold"))
            btn_x.config(bg="#eaeaea", fg="black", relief=tk.FLAT, font=("Arial", 9))
        else:
            btn_y.config(bg="#eaeaea", fg="black", relief=tk.FLAT, font=("Arial", 9))
            btn_x.config(bg="#4a90e2", fg="white", relief=tk.RAISED, font=("Arial", 9, "bold"))
        trigger_plane_redraw()

    btn_y.config(command=lambda: set_strategy("Зигзаг по Y"))
    btn_x.config(command=lambda: set_strategy("Зигзаг по X"))

    controller.active_inputs = entries
    controller.active_inputs["strategy_var"] = strategy_var

    # Первичный запуск отрисовки
    canvas.bind("<Configure>", lambda e: trigger_plane_redraw())
    trigger_plane_redraw()


def generate_plane_gcode(inputs):
    """
    🤖 ЧИСТАЯ МАТЕМАТИКА ЧПУ: Рассчитывает пошаговую змейку УП 
    для идеального бритья жертвенного стола или щита фрезой-летучкой!
    """
    try:
        size_y = float(inputs["size_y"].get())
        size_x = float(inputs["size_x"].get())
        tool_d = float(inputs["tool_d"].get())
        overlap_pct = float(inputs["overlap"].get())
        z_deep = float(inputs["z_deep"].get())
        feed_f = int(inputs["feed_f"].get())
        strategy = inputs["strategy_var"].get()
    except (ValueError, KeyError):
        return ["G21 G90", "( Ошибка числовых параметров )", "M30"]

    # Вычисляем рабочий шаг смещения фрезы в мм с учетом перекрытия проходов
    # Шаг = Диаметр * (100% - Перекрытие%) / 100
    step_mm = tool_d * (1.0 - (overlap_pct / 100.0))
    if step_mm <= 1.0: step_mm = 5.0 # Защита от бесконечного цикла

    gcode = ["G21 G49 G80 G90 G91.1", f"( --- ВЫРАВНИВАНИЕ ПЛОСКОСТИ СТОЛА {int(size_y)}x{int(size_x)} --- )", "G0 Z50.000"]
    gcode.append(f"G0 X0.000 Y0.000 S12000 M3") # Включаем шпиндель (для больших фрез обороты поменьше, 12000)
    gcode.append(f"G1 Z{z_deep:.3f} F500")

    # ГЕНЕРАЦИЯ ТРАЕКТОРИИ ЗМЕЙКИ ВДОЛЬ ОСИ Y
    if strategy == "Зигзаг по Y":
        curr_x = 0.0
        direction = 1 # 1 = едем вперед по Y, -1 = едем назад по Y
        
        while curr_x <= size_x:
            if direction == 1:
                gcode.append(f"G1 X{curr_x:.3f} Y{size_y:.3f} F{feed_f}")
                direction = -1
            else:
                gcode.append(f"G1 X{curr_x:.3f} Y0.000 F{feed_f}")
                direction = 1
                
            curr_x += step_mm
            if curr_x <= size_x:
                gcode.append(f"G1 X{curr_x:.3f}") # Делаем боковое смещение на следующий ряд
                
    # ГЕНЕРАЦИЯ ТРАЕКТОРИИ ЗМЕЙКИ ВДОЛЬ ОСИ X
    else:
        curr_y = 0.0
        direction = 1
        while curr_y <= size_y:
            if direction == 1:
                gcode.append(f"G1 X{size_x:.3f} Y{curr_y:.3f} F{feed_f}")
                direction = -1
            else:
                gcode.append(f"G1 X0.000 Y{curr_y:.3f} F{feed_f}")
                direction = 1
                
            curr_y += step_mm
            if curr_y <= size_y:
                gcode.append(f"G1 Y{curr_y:.3f}")

    gcode.append("G0 Z50.000")
    gcode.append("G0 X0.000 Y0.000\nM5\nM30")
    return gcode
