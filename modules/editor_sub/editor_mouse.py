import tkinter as tk
from tkinter import ttk
from modules.editor_sub import editor_engine

def init_mouse_logic(canvas, state):
    """
    ЧИСТОВАЯ СБОРКА: Интерактивное CAD-ядро мыши.
    Полностью изолирует логику векторов, магнитный прицел и маркеры текста Варианта B.
    """
    # Секция 1: Единая системная память мыши
    start_x, start_y = None, None
    temp_item = None        
    dragged_item = None     
    snap_marker = None      

    def on_global_click_check(event):
        """Проверяет клик мимо активного окна ввода или пустую область миллиметровки"""
        nonlocal start_x, start_y, temp_item, dragged_item, snap_marker
        if hasattr(canvas, 'current_text_context') and canvas.current_text_context:
            closest = canvas.find_closest(event.x, event.y)
            ctx = canvas.current_text_context
            if ctx["window_id"] not in closest:
                finalize_text_input()
                
        # Если кликнули в абсолютно пустое место, стираем маркеры Варианта B
        closest = canvas.find_closest(event.x, event.y, halo=5)
        if not closest or all("grid_line" in canvas.gettags(i) for i in closest):
            canvas.delete("text_handle")

    def update_snap_visualization(event):
        """Рассчитывает и подсвечивает зеленый перекрестный прицел магнитной привязки"""
        nonlocal start_x, start_y, temp_item, dragged_item, snap_marker
        if snap_marker: 
            canvas.delete(snap_marker)
            snap_marker = None
            
        tool = state["active_tool"].get()
        if tool in ["line", "rect", "oval"]:
            is_snapped, snap_x, snap_y = editor_engine.find_nearest_snap_point(canvas, event.x, event.y, snap_radius=15)
            if is_snapped:
                r = 6
                canvas.create_line(snap_x - r, snap_y, snap_x + r, snap_y, fill="#28a745", width=2)
                canvas.create_line(snap_x, snap_y - r, snap_x, snap_y + r, fill="#28a745", width=2)
                snap_marker = canvas.create_rectangle(snap_x - 3, snap_y - 3, snap_x + 3, snap_y + 3, outline="#28a745", width=1)
                return True, snap_x, snap_y
        return False, event.x, event.y
    def on_click(event):
        """Обрабатывает нажатие ЛКМ, включает CAD-защиту текста и строит маркеры размера"""
        on_global_click_check(event) # Первым делом проверяем закрытие старых сессий
        nonlocal start_x, start_y, temp_item, dragged_item, snap_marker
        
        is_snapped, use_x, os_y = update_snap_visualization(event)
        start_x = use_x if is_snapped else event.x
        start_y = os_y if is_snapped else event.y
        
        tool = state["active_tool"].get()
        canvas.delete("text_handle") # Стираем старые маркеры при новом клике
        
        # Исправлено: заменили canvas.exists на стабильный поиск find_withtag
        if state["selected_id"] and canvas.find_withtag(state["selected_id"]):
            try:
                if canvas.type(state["selected_id"]) == "text":
                    canvas.itemconfig(state["selected_id"], fill="#1d4182")
                else:
                    canvas.itemconfig(state["selected_id"], fill="#1d4182" if canvas.type(state["selected_id"]) != "rectangle" else "")
                    if canvas.type(state["selected_id"]) in ["rectangle", "oval"]:
                        canvas.itemconfig(state["selected_id"], outline="#1d4182")
            except Exception: pass
        
        if tool == "move_item":
            closest = canvas.find_closest(event.x, event.y, halo=15)
            if closest:
                item_id = closest if isinstance(closest, tuple) else closest
                tags = canvas.gettags(item_id)
                
                if "grid_line" not in tags and "joystick_window" not in tags:
                    if "text_handle" in tags:
                        dragged_item = item_id
                        return
                        
                    dragged_item = item_id
                    state["selected_id"] = item_id
                    
                    # ЧИСТАЯ CAD-ИЗОЛЯЦИЯ ТЕКСТА ОТ ИЗМЕНЕНИЯ ШИРИНЫ WIDTH
                    if canvas.type(dragged_item) == "text":
                        # Меняем ТОЛЬКО цвет букв. Ширину (width) не трогаем вообще!
                        canvas.itemconfig(dragged_item, fill="#4a90e2")
                        
                        bbox = canvas.bbox(dragged_item)
                        if bbox:
                            bx1, by1, bx2, by2 = bbox
                            r = 4
                            # Системный тег родителя с правильным разделителем для Шага 2
                            parent_tag = f"parent_{dragged_item}"
                            
                            # Строим маркеры Варианта B строго по краям реального bbox текста
                            canvas.create_rectangle(bx2 - r, ((by1 + by2) / 2) - r, bx2 + r, ((by1 + by2) / 2) + r, fill="#4a90e2", outline="#ffffff", tags=("text_handle", "width_handle", parent_tag))
                            canvas.create_rectangle(((bx1 + bx2) / 2) - r, by2 - r, ((bx1 + bx2) / 2) + r, by2 + r, fill="#4a90e2", outline="#ffffff", tags=("text_handle", "height_handle", parent_tag))
                    else:
                        # Эта ветка выполняется ТОЛЬКО для линий, прямоугольников и окружностей
                        canvas.itemconfig(dragged_item, width=3)
                        if canvas.type(dragged_item) in ["rectangle", "oval"]:
                            canvas.itemconfig(dragged_item, outline="#4a90e2")
                        else:
                            canvas.itemconfig(dragged_item, fill="#4a90e2")
                            
        elif tool == "text":
            temp_item = None

    def on_drag(event):
        """Динамическое масштабирование рамок текста за маркеры и черчение фигур"""
        nonlocal start_x, start_y, temp_item, dragged_item, snap_marker
        if start_x is None or start_y is None: return
        
        tool = state["active_tool"].get()
        is_snapped, use_x, os_y = update_snap_visualization(event)
        current_target_x = use_x if is_snapped else event.x
        current_target_y = os_y if is_snapped else event.y
        
        if tool == "move_item" and dragged_item is not None:
            tags = canvas.gettags(dragged_item)
            
            # --- РАСТЯГИВАНИЕ CAD-МАРКЕРОВ ВАРИАНТА B ЧЕРЕЗ ТЕГИ ---
            if "text_handle" in tags:
                text_id = None
                # Исправлено: корректно извлекаем числовой ID текста из списка сплита [1]
                for tag in tags:
                    if tag.startswith("parent_"):
                        try:
                            text_id = int(tag.split("_")[1])
                            break
                        except Exception: pass
                        
                if not text_id or not canvas.find_withtag(text_id): return
                
                bbox = canvas.bbox(text_id)
                if not bbox: return
                bx1, by1, bx2, by2 = bbox
                
                if "width_handle" in tags:
                    new_w = max(20, event.x - bx1)
                    canvas.itemconfig(text_id, width=new_w)
                    canvas.coords(dragged_item, event.x - 4, ((by1 + by2) / 2) - 4, event.x + 4, ((by1 + by2) / 2) + 4)
                    
                    new_bbox = canvas.bbox(text_id)
                    if new_bbox:
                        nbx1, nby1, nbx2, nby2 = new_bbox
                        for h_id in canvas.find_withtag("height_handle"):
                            h_tags = canvas.gettags(h_id)
                            if f"parent_{text_id}" in h_tags:
                                canvas.coords(h_id, ((nbx1 + nbx2) / 2) - 4, nby2 - 4, ((nbx1 + nbx2) / 2) + 4, nby2 + 4)
                                
                elif "height_handle" in tags:
                    canvas.coords(dragged_item, ((bx1 + bx2) / 2) - 4, event.y - 4, ((bx1 + bx2) / 2) + 4, event.y + 4)
                
                new_bbox = canvas.bbox(text_id)
                if new_bbox:
                    for elem in editor_engine.DRAWN_ELEMENTS:
                        if elem.get("id") == text_id:
                            elem["coords"] = list(new_bbox)
                            break
                return

            dx = event.x - start_x
            dy = event.y - start_y
            canvas.move(dragged_item, dx, dy)
            
            if canvas.type(dragged_item) == "text":
                canvas.delete("text_handle")
            
            for elem in editor_engine.DRAWN_ELEMENTS:
                if elem.get("id") == dragged_item:
                    if "coords" in elem:
                        elem["coords"] = [c + (dx if idx % 2 == 0 else dy) for idx, c in enumerate(elem["coords"])]
                    break
            start_x = event.x
            start_y = event.y
            
        elif tool == "line":
            if temp_item: canvas.delete(temp_item)
            temp_item = canvas.create_line(start_x, start_y, current_target_x, current_target_y, fill="#1d4182", width=2, tags="drawn_line")
            
        elif tool == "rect":
            if temp_item: canvas.delete(temp_item)
            temp_item = canvas.create_rectangle(start_x, start_y, current_target_x, current_target_y, outline="#1d4182", width=2, tags="drawn_line")
            
        elif tool == "oval":
            if temp_item: canvas.delete(temp_item)
            temp_item = canvas.create_oval(start_x, start_y, current_target_x, current_target_y, outline="#1d4182", width=2, tags="drawn_line")
            
        elif tool == "text":
            if temp_item: canvas.delete(temp_item)
            temp_item = canvas.create_rectangle(start_x, start_y, current_target_x, current_target_y, outline="#4a90e2", dash=(4, 2), tags="temp_text_frame")
            
        elif tool == "pan":
            dx = event.x - start_x
            dy = event.y - start_y
            state["pan_x"] += dx
            state["pan_y"] += dy
            canvas.move("drawn_line", dx, dy)
            canvas.move("vector_text", dx, dy)
            canvas.move("dxf_group", dx, dy)
            editor_engine.draw_editor_grid(canvas, canvas.winfo_width(), canvas.winfo_height(), 10, state["pan_x"], state["pan_y"])
            start_x = event.x
            start_y = event.y

    def on_release(event):
        """Фиксирует нарисованные контуры или открывает встроенный текстовый блок"""
        nonlocal start_x, start_y, temp_item, dragged_item, snap_marker
        tool = state["active_tool"].get()
        
        if dragged_item and "text_handle" in canvas.gettags(dragged_item):
            dragged_item = None
            return

        if tool == "text" and temp_item:
            x1, y1, x2, y2 = canvas.coords(temp_item)
            w, h = abs(x2 - x1), abs(y2 - y1)
            
            if w > 15 and h > 15:
                combo_font, ent_font_size = canvas.text_entry_widgets
                font_name = combo_font.get()
                try: font_size = int(ent_font_size.get())
                except ValueError: font_size = 14

                text_input = tk.Text(canvas, wrap=tk.WORD, font=(font_name, font_size), bd=1, relief=tk.SOLID, bg="#ffffff")
                input_window = canvas.create_window(min(x1, x2), min(y1, y2), window=text_input, width=w, height=h, anchor=tk.NW, tags="active_text_input_win")
                text_input.focus_set()
                
                canvas.current_text_context = {
                    "frame_id": temp_item, "window_id": input_window, "text_widget": text_input,
                    "coords": [x1, y1, x2, y2], "font_name": font_name, "font_size": font_size
                }
                temp_item = None
                return
            else:
                canvas.delete(temp_item)
                temp_item = None

        elif tool in ["line", "rect", "oval"] and temp_item:
            c = canvas.coords(temp_item)
            editor_engine.DRAWN_ELEMENTS.append({
                "type": "line" if tool == "line" else ("rect" if tool == "rect" else "oval"),
                "id": temp_item, "coords": c
            })
            temp_item = None

        if dragged_item is not None:
            try: canvas.itemconfig(dragged_item, width=2)
            except Exception: pass
            dragged_item = None
        if snap_marker:
            canvas.delete(snap_marker)
            snap_marker = None

    def finalize_text_input(event=None):
        """Очищает память мыши и фиксирует буквы с тегом vector_text и жесткой шириной"""
        nonlocal start_x, start_y, temp_item, dragged_item, snap_marker
        if not hasattr(canvas, 'current_text_context') or not canvas.current_text_context: return
        ctx = canvas.current_text_context
        raw_text = ctx["text_widget"].get("1.0", tk.END).strip()
        
        canvas.delete(ctx["window_id"])
        canvas.delete(ctx["frame_id"])
        canvas.current_text_context = None
        
        # Полное обнуление сессии черчения
        start_x, start_y, temp_item = None, None, None
        
        if raw_text:
            x1, y1, x2, y2 = ctx["coords"]
            w = abs(x2 - x1)
            
            final_text_id = canvas.create_text(
                min(x1, x2), min(y1, y2), text=raw_text, font=(ctx["font_name"], ctx["font_size"]),
                fill="#1d4182", anchor=tk.NW, width=w, justify=tk.LEFT, tags="vector_text"
            )
            
            editor_engine.DRAWN_ELEMENTS.append({
                "type": "text", "id": final_text_id, "text": raw_text,
                "coords": [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)],
                "font_name": ctx["font_name"], "font_size": ctx["font_size"]
            })
            
        state["active_tool"].set("move_item")
        if hasattr(canvas, 'toolbar_buttons_cache'):
            for b in canvas.toolbar_buttons_cache.values(): b.config(bg="#ffffff", fg="black", font=("Arial", 9))
            canvas.toolbar_buttons_cache["move_item"].config(bg="#4a90e2", fg="white", font=("Arial", 9, "bold"))

    # --- СЕКЦИЯ МОНОЛИТНЫХ СИСТЕМНЫХ ПРИВЯЗОК ---
    canvas.bind("<Motion>", update_snap_visualization)
    canvas.bind("<Button-1>", on_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    # CAD-перехватчик горячей клавиши Enter для завершения ввода
    canvas.bind_all("<Return>", lambda e: finalize_text_input() if hasattr(canvas, 'current_text_context') and canvas.current_text_context else None)

    # --- КОНТЕКСТНОЕ МЕНЮ ПКМ И ОКНО СВОЙСТВ ---
    ctx_menu = tk.Menu(canvas, tearoff=0, font=("Arial", 10), bg="#ffffff")

    def open_properties_window():
        if not state["selected_id"]: return
        target_elem = None
        for elem in editor_engine.DRAWN_ELEMENTS:
            if elem.get("id") == state["selected_id"]:
                target_elem = elem
                break
        if not target_elem: return

        win = tk.Toplevel(canvas)
        win.title(" Свойства элемента ЧПУ ")
        win.geometry("280x200")
        win.resizable(False, False)
        win.grab_set()

        ttk.Label(win, text="Точка X1 / X (мм):").grid(row=0, column=0, padx=15, pady=6, sticky=tk.W)
        ent_x1 = ttk.Entry(win, width=12)
        ent_x1.insert(0, f"{target_elem['coords']:.2f}")
        ent_x1.grid(row=0, column=1, padx=15, pady=6)

        ttk.Label(win, text="Точка Y1 / Y (мм):").grid(row=1, column=0, padx=15, pady=6, sticky=tk.W)
        ent_y1 = ttk.Entry(win, width=12)
        ent_y1.insert(0, f"{target_elem['coords']:.2f}")
        ent_y1.grid(row=1, column=1, padx=15, pady=6)

        ttk.Label(win, text="Точка X2 / W (мм):").grid(row=2, column=0, padx=15, pady=6, sticky=tk.W)
        ent_x2 = ttk.Entry(win, width=12)
        ent_x2.insert(0, f"{target_elem['coords']:.2f}")
        ent_x2.grid(row=2, column=1, padx=15, pady=6)

        ttk.Label(win, text="Точка Y2 / H (мм):").grid(row=3, column=0, padx=15, pady=6, sticky=tk.W)
        ent_y2 = ttk.Entry(win, width=12)
        ent_y2.insert(0, f"{target_elem['coords']:.2f}")
        ent_y2.grid(row=3, column=1, padx=15, pady=6)

        def apply_manual_coordinates():
            try:
                new_c = [float(ent_x1.get()), float(ent_y1.get()), float(ent_x2.get()), float(ent_y2.get())]
                target_elem["coords"] = new_c
                canvas.coords(state["selected_id"], *new_c)
                if canvas.type(state["selected_id"]) == "text":
                    canvas.delete("text_handle")
                win.destroy()
            except ValueError: pass

        btn_apply = tk.Button(win, text="ПРИМЕНИТЬ РАЗМЕРЫ", bg="#4a90e2", fg="white", font=("Arial", 9, "bold"), bd=0, height=2, command=apply_manual_coordinates)
        btn_apply.grid(row=4, column=0, columnspan=2, sticky="ew", padx=15, pady=10)

    def show_context_menu(event):
        ctx_menu.delete(0, tk.END)
        mm_x = int(event.x - state["pan_x"])
        mm_y = int(event.y - state["pan_y"])
        ctx_menu.add_command(label=f" Координаты мыши: X={mm_x}мм, Y={mm_y}мм ", state="disabled")
        ctx_menu.add_separator()
        
        if state["selected_id"]:
            ctx_menu.add_command(label="📊 Открыть свойства геометрии", command=open_properties_window)
            if hasattr(canvas, 'clipboard_commands_cache'):
                action_copy, action_cut, _ = canvas.clipboard_commands_cache
                ctx_menu.add_command(label="📄 Скопировать деталь", command=action_copy)
                ctx_menu.add_command(label="✂️ Вырезать деталь", command=action_cut)
        else:
            ctx_menu.add_command(label="📊 Свойства (Элемент не выбран)", state="disabled")
            if hasattr(canvas, 'clipboard_commands_cache'):
                _, _, action_paste = canvas.clipboard_commands_cache
                from modules.editor_sub.editor_toolbar import EDITOR_CLIPBOARD
                if EDITOR_CLIPBOARD:
                    ctx_menu.add_command(label="📥 Вставить элемент сюда", command=action_paste)
                
        ctx_menu.post(event.x_root, event.y_root)

    canvas.bind("<Button-3>", show_context_menu)
