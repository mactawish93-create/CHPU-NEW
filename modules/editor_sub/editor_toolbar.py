import tkinter as tk
from tkinter import ttk
import os
from modules.editor_sub import editor_engine

# Глобальный буфер обмена для копирования и вставки деталей ЧПУ станка
EDITOR_CLIPBOARD = None

def build_toolbar(parent_frame, canvas, state):
    """
    ЭТАЛОННАЯ СБОРКА: Монолитный тулбар ЧПУ с графическими иконками 24х24.
    Изолирует ссылки на картинки в памяти canvas, предотвращая их невидимое удаление.
    """
    # Создаем защищенный контейнер для картинок прямо внутри объекта canvas,
    # чтобы сборщик мусора Python (Garbage Collector) никогда не удалял их из памяти!
    if not hasattr(canvas, "toolbar_images_cache"):
        canvas.toolbar_images_cache = {}

    def load_icon(file_name, backup_text):
        """
        Безопасно загружает иконку 24х24 из папки icons.
        Если файл отсутствует — возвращает текст, защищая программу от аварийного вылета.
        """
        icon_path = os.path.join("icons", file_name)
        if os.path.exists(icon_path):
            try:
                # Загружаем картинку и намертво кэшируем её в памяти холста
                img = tk.PhotoImage(file=icon_path)
                canvas.toolbar_images_cache[file_name] = img
                return img
            except Exception:
                pass
        # Если графики нет — возвращаем текстовую заглушку
        return backup_text

    # Настраиваем стиль разделителей (Separator) между блоками для красивых черных линий
    style = ttk.Style()
    style.configure("Toolbar.TSeparator", background="#000000")

    # Сетка кэша для кнопок, чтобы мышь могла подсвечивать активные инструменты
    canvas.toolbar_buttons_cache = {}

    def set_active_tool(tool_name):
        """Интеллектуальная подсветка активного инструмента на панели ЧПУ станка"""
        state["active_tool"].set(tool_name)
        for name, btn in canvas.toolbar_buttons_cache.items():
            if name == tool_name:
                btn.config(bg="#4a90e2", fg="white") # Яркий CAD-акцент для выбранного режима
            else:
                btn.config(bg="#ffffff", fg="black")

    # ==========================================
    # БЛОК 1: УПРАВЛЕНИЕ ПРОЕКТАМИ (ФАЙЛЫ .CAM)
    # ==========================================
    img_new = load_icon("new_file.png", "Новый")
    img_open = load_icon("open_file.png", "Открыть")
    img_save = load_icon("save_file.png", "Сохр.")

    btn_new = tk.Button(parent_frame, image=img_new if isinstance(img_new, tk.PhotoImage) else None, text="" if isinstance(img_new, tk.PhotoImage) else img_new, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=lambda: editor_engine.clear_project(canvas))
    btn_new.pack(side=tk.LEFT, padx=2)
    
    btn_open = tk.Button(parent_frame, image=img_open if isinstance(img_open, tk.PhotoImage) else None, text="" if isinstance(img_open, tk.PhotoImage) else img_open, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=lambda: editor_engine.open_project_cam(canvas))
    btn_open.pack(side=tk.LEFT, padx=2)
    
    btn_save = tk.Button(parent_frame, image=img_save if isinstance(img_save, tk.PhotoImage) else None, text="" if isinstance(img_save, tk.PhotoImage) else img_save, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=lambda: editor_engine.save_project_cam(canvas))
    btn_save.pack(side=tk.LEFT, padx=2)

    sep1 = ttk.Separator(parent_frame, orient=tk.VERTICAL, style="Toolbar.TSeparator")
    sep1.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=4)
    # ==========================================
    # БЛОК 2: ГРАВИРОВКА ТЕКСТА И ШРИФТЫ
    # ==========================================
    img_text = load_icon("text.png", "Текст")
    btn_text = tk.Button(parent_frame, image=img_text if isinstance(img_text, tk.PhotoImage) else None, text="" if isinstance(img_text, tk.PhotoImage) else img_text, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=lambda: set_active_tool("text"))
    btn_text.pack(side=tk.LEFT, padx=2)
    canvas.toolbar_buttons_cache["text"] = btn_text

    # Выпадающий список системных шрифтов
    combo_font = ttk.Combobox(parent_frame, values=["Arial", "Courier New", "Times New Roman", "Segoe UI"], width=12, state="readonly")
    combo_font.set("Arial")
    combo_font.pack(side=tk.LEFT, padx=4, pady=4)

    # Выпадающий список размеров символов
    combo_size = ttk.Combobox(parent_frame, values=["10", "12", "14", "16", "20", "24", "28", "36", "48"], width=4, state="readonly")
    combo_size.set("14")
    combo_size.pack(side=tk.LEFT, padx=2, pady=4)
    
    # Сохраняем ссылки на виджеты в холст для быстрого доступа из editor_mouse.py
    canvas.text_entry_widgets = (combo_font, combo_size)

    sep2 = ttk.Separator(parent_frame, orient=tk.VERTICAL, style="Toolbar.TSeparator")
    sep2.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=4)

    # ==========================================
    # БЛОК 3: ИНСТРУМЕНТЫ ГЕОМЕТРИИ И КОНТУРОВ
    # ==========================================
    img_rect = load_icon("rect.png", "Паз")
    img_oval = load_icon("oval.png", "Круг")
    img_line = load_icon("line.png", "Линия")
    img_arc = load_icon("arc.png", "Дуга")

    btn_rect = tk.Button(parent_frame, image=img_rect if isinstance(img_rect, tk.PhotoImage) else None, text="" if isinstance(img_rect, tk.PhotoImage) else img_rect, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=lambda: set_active_tool("rect"))
    btn_rect.pack(side=tk.LEFT, padx=2)
    canvas.toolbar_buttons_cache["rect"] = btn_rect

    btn_oval = tk.Button(parent_frame, image=img_oval if isinstance(img_oval, tk.PhotoImage) else None, text="" if isinstance(img_oval, tk.PhotoImage) else img_oval, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=lambda: set_active_tool("oval"))
    btn_oval.pack(side=tk.LEFT, padx=2)
    canvas.toolbar_buttons_cache["oval"] = btn_oval

    btn_line = tk.Button(parent_frame, image=img_line if isinstance(img_line, tk.PhotoImage) else None, text="" if isinstance(img_line, tk.PhotoImage) else img_line, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=lambda: set_active_tool("line"))
    btn_line.pack(side=tk.LEFT, padx=2)
    canvas.toolbar_buttons_cache["line"] = btn_line

    btn_arc = tk.Button(parent_frame, image=img_arc if isinstance(img_arc, tk.PhotoImage) else None, text="" if isinstance(img_arc, tk.PhotoImage) else img_arc, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=lambda: set_active_tool("arc"))
    btn_arc.pack(side=tk.LEFT, padx=2)
    canvas.toolbar_buttons_cache["arc"] = btn_arc

    sep3 = ttk.Separator(parent_frame, orient=tk.VERTICAL, style="Toolbar.TSeparator")
    sep3.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=4)

    # ==========================================
    # БЛОК 4: МАНИПУЛЯЦИИ И CAD-НАВИГАЦИЯ
    # ==========================================
    img_move = load_icon("move_item.png", "Стрелка")
    img_pan = load_icon("pan.png", "Рука")

    btn_move = tk.Button(parent_frame, image=img_move if isinstance(img_move, tk.PhotoImage) else None, text="" if isinstance(img_move, tk.PhotoImage) else img_move, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=lambda: set_active_tool("move_item"))
    btn_move.pack(side=tk.LEFT, padx=2)
    canvas.toolbar_buttons_cache["move_item"] = btn_move

    btn_pan = tk.Button(parent_frame, image=img_pan if isinstance(img_pan, tk.PhotoImage) else None, text="" if isinstance(img_pan, tk.PhotoImage) else img_pan, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=lambda: set_active_tool("pan"))
    btn_pan.pack(side=tk.LEFT, padx=2)
    canvas.toolbar_buttons_cache["pan"] = btn_pan

    # Инициализируем стартовую подсветку: по умолчанию активна стрелочка выделения
    set_active_tool("move_item")

    sep4 = ttk.Separator(parent_frame, orient=tk.VERTICAL, style="Toolbar.TSeparator")
    sep4.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=4)
    # ==========================================
    # БЛОК 5: РЕЖИМЫ И НАСТРОЙКИ ЧПУ (2 КНОПКИ)
    # ==========================================
    img_cnc_set = load_icon("cnc_settings.png", "ЧПУ")
    img_cnc_blk = load_icon("cnc_blank.png", "—")

    # Функция-заглушка для окна расширенных настроек станка фрез
    def open_cnc_parameters():
        win = tk.Toplevel(canvas)
        win.title(" Параметры ЧПУ фрезерования ")
        win.geometry("260x150")
        win.resizable(False, False)
        win.grab_set()
        ttk.Label(win, text="Диаметр фрезы (мм):").pack(pady=10)
        ttk.Entry(win, width=15).pack()
        ttk.Button(win, text="Сохранить", command=win.destroy).pack(pady=15)

    btn_cnc_set = tk.Button(parent_frame, image=img_cnc_set if isinstance(img_cnc_set, tk.PhotoImage) else None, text="" if isinstance(img_cnc_set, tk.PhotoImage) else img_cnc_set, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=open_cnc_parameters)
    btn_cnc_set.pack(side=tk.LEFT, padx=2)
    
    btn_cnc_blk = tk.Button(parent_frame, image=img_cnc_blk if isinstance(img_cnc_blk, tk.PhotoImage) else None, text="" if isinstance(img_cnc_blk, tk.PhotoImage) else img_cnc_blk, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, state="disabled")
    btn_cnc_blk.pack(side=tk.LEFT, padx=2)

    sep5 = ttk.Separator(parent_frame, orient=tk.VERTICAL, style="Toolbar.TSeparator")
    sep5.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=4)

    # ==========================================
    # БЛОК 6: РЕДАКТИРОВАНИЕ И БУФЕР ОБМЕНА
    # ==========================================
    img_copy = load_icon("copy.png", "Копир.")
    img_cut = load_icon("cut.png", "Вырез.")
    img_paste = load_icon("paste.png", "Встав.")

    def action_copy_item():
        global EDITOR_CLIPBOARD
        if state["selected_id"] and canvas.find_withtag(state["selected_id"]):
            for elem in editor_engine.DRAWN_ELEMENTS:
                if elem.get("id") == state["selected_id"]:
                    import copy
                    EDITOR_CLIPBOARD = copy.deepcopy(elem)
                    break

    def action_cut_item():
        global EDITOR_CLIPBOARD
        if state["selected_id"] and canvas.find_withtag(state["selected_id"]):
            action_copy_item()
            canvas.delete(state["selected_id"])
            canvas.delete("text_handle")
            editor_engine.DRAWN_ELEMENTS = [e for e in editor_engine.DRAWN_ELEMENTS if e.get("id") != state["selected_id"]]
            state["selected_id"] = None

    def action_paste_item():
        global EDITOR_CLIPBOARD
        if EDITOR_CLIPBOARD:
            import copy
            new_elem = copy.deepcopy(EDITOR_CLIPBOARD)
            
            # Смещаем вставляемую деталь чуть в сторону от оригинала
            if "coords" in new_elem:
                new_elem["coords"] = [c + 20 for c in new_elem["coords"]]
            
            if new_elem["type"] == "line":
                new_id = canvas.create_line(*new_elem["coords"], fill="#1d4182", width=2, tags="drawn_line")
            elif new_elem["type"] == "rect":
                new_id = canvas.create_rectangle(*new_elem["coords"], outline="#1d4182", width=2, tags="drawn_line")
            elif new_elem["type"] == "oval":
                new_id = canvas.create_oval(*new_elem["coords"], outline="#1d4182", width=2, tags="drawn_line")
            elif new_elem["type"] == "text":
                x1, y1, x2, y2 = new_elem["coords"]
                new_id = canvas.create_text(x1, y1, text=new_elem["text"], font=(new_elem["font_name"], new_elem["font_size"]), fill="#1d4182", anchor=tk.NW, width=abs(x2 - x1), tags="vector_text")
                new_elem["text"] = EDITOR_CLIPBOARD["text"]
                new_elem["font_name"] = EDITOR_CLIPBOARD["font_name"]
                new_elem["font_size"] = EDITOR_CLIPBOARD["font_size"]
                
            new_elem["id"] = new_id
            editor_engine.DRAWN_ELEMENTS.append(new_elem)
            state["selected_id"] = new_id

    btn_copy = tk.Button(parent_frame, image=img_copy if isinstance(img_copy, tk.PhotoImage) else None, text="" if isinstance(img_copy, tk.PhotoImage) else img_copy, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=action_copy_item)
    btn_copy.pack(side=tk.LEFT, padx=2)
    
    btn_cut = tk.Button(parent_frame, image=img_cut if isinstance(img_cut, tk.PhotoImage) else None, text="" if isinstance(img_cut, tk.PhotoImage) else img_cut, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=action_cut_item)
    btn_cut.pack(side=tk.LEFT, padx=2)
    
    btn_paste = tk.Button(parent_frame, image=img_paste if isinstance(img_paste, tk.PhotoImage) else None, text="" if isinstance(img_paste, tk.PhotoImage) else img_paste, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=action_paste_item)
    btn_paste.pack(side=tk.LEFT, padx=2)

    # Кэшируем команды для вызова контекстного ПКМ-меню в editor_mouse.py
    canvas.clipboard_commands_cache = (action_copy_item, action_cut_item, action_paste_item)

    sep6 = ttk.Separator(parent_frame, orient=tk.VERTICAL, style="Toolbar.TSeparator")
    sep6.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=4)

    # ==========================================
    # БЛОК 7: ИМПОРТ И ЭКСПОРТ (3 КНОПКИ)
    # ==========================================
    img_exp_dxf = load_icon("export_dxf.png", "E-DXF")
    img_exp_tap = load_icon("export_tap.png", "E-TAP")
    img_imp_dxf = load_icon("import_dxf.png", "I-DXF")

    btn_exp_dxf = tk.Button(parent_frame, image=img_exp_dxf if isinstance(img_exp_dxf, tk.PhotoImage) else None, text="" if isinstance(img_exp_dxf, tk.PhotoImage) else img_exp_dxf, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=lambda: editor_engine.export_project_dxf(canvas))
    btn_exp_dxf.pack(side=tk.LEFT, padx=2)
    
    btn_exp_tap = tk.Button(parent_frame, image=img_exp_tap if isinstance(img_exp_tap, tk.PhotoImage) else None, text="" if isinstance(img_exp_tap, tk.PhotoImage) else img_exp_tap, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=lambda: editor_engine.export_project_tap(canvas))
    btn_exp_tap.pack(side=tk.LEFT, padx=2)
    
    btn_imp_dxf = tk.Button(parent_frame, image=img_imp_dxf if isinstance(img_imp_dxf, tk.PhotoImage) else None, text="" if isinstance(img_imp_dxf, tk.PhotoImage) else img_imp_dxf, bg="#ffffff", bd=1, relief=tk.FLAT, width=32, height=32, command=lambda: editor_engine.import_project_dxf(canvas))
    btn_imp_dxf.pack(side=tk.LEFT, padx=2)
