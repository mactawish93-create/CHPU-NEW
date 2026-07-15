import tkinter as tk
from tkinter import ttk
import os
from modules.editor_sub import editor_engine

def get_resource_path(relative_path):
    """Определитель путей к файлам для разработки и для сборки в .exe"""
    import sys
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def create_joystick_button(parent, icon_filename, default_text, command_func=None):
    """Ищет PNG в папке icons. Если файла нет — выводит текстовую кнопку-стрелочку"""
    icon_path = get_resource_path(os.path.join("icons", icon_filename))
    
    btn_kwargs = {
        "text": default_text,
        "bg": "#ffffff", 
        "bd": 1, 
        "relief": tk.GROOVE, 
        "width": 3,
        "height": 1,
        "cursor": "hand2",
        "font": ("Arial", 10, "bold")
    }
    if command_func: 
        btn_kwargs["command"] = command_func
        
    if os.path.exists(icon_path):
        try:
            img = tk.PhotoImage(file=icon_path)
            btn = tk.Button(parent, image=img, bg="#ffffff", bd=1, relief=tk.GROOVE, cursor="hand2")
            btn.image = img 
            return btn
        except Exception: 
            pass
            
    return tk.Button(parent, **btn_kwargs)

def build_joystick(canvas, state, w_width, w_height):
    """Собирает плавающий матричный джойстик навигации 3х3 по CAD-чертежу"""
    
    # Создаем контейнер-фрейм для матрицы кнопок
    joystick_frame = tk.Frame(canvas, bg="#eaeaea", bd=1, relief=tk.GROOVE)
    joystick_win = canvas.create_window(w_width - 20, w_height - 20, window=joystick_frame, anchor=tk.SE, tags="joystick_window")

    # --- НОВАЯ ИНЖЕНЕРНАЯ ПЛАШКА МАСШТАБА ---
    # Создаем текстовую метку на самом верху джойстика
    lbl_scale_text = tk.Label(
        joystick_frame, 
        text=f"Зум: {int(state['scale'])}%", 
        bg="#eaeaea", 
        font=("Arial", 8, "bold"),
        fg="#333333"
    )
    lbl_scale_text.grid(row=0, column=0, columnspan=3, pady=(2, 4), sticky="ew")

    def move_panorama(direction):
        """Сдвиг панорамы стола на фиксированный шаг 50 мм по стрелкам джойстика"""
        step = 50
        if direction == "up": state["pan_y"] += step
        elif direction == "down": state["pan_y"] -= step
        elif direction == "left": state["pan_x"] += step
        elif direction == "right": state["pan_x"] -= step
        elif direction == "center": 
            state["pan_x"], state["pan_y"] = 0, 0
            state["scale"] = 100.0
            lbl_scale_text.config(text="Зум: 100%") # Сбрасываем текст плашки
            canvas.delete("drawn_line", "vector_text", "dxf_group")
            editor_engine.DRAWN_ELEMENTS = []
            editor_engine.HISTORY_REDO = []
            editor_engine.draw_editor_grid(canvas, canvas.winfo_width(), canvas.winfo_height(), 10, 0, 0)
            return
        
        dx = step if direction == "left" else (-step if direction == "right" else 0)
        dy = step if direction == "up" else (-step if direction == "down" else 0)
            
        canvas.move("drawn_line", dx, dy)
        canvas.move("vector_text", dx, dy)
        canvas.move("dxf_group", dx, dy)
        editor_engine.draw_editor_grid(canvas, canvas.winfo_width(), canvas.winfo_height(), 10, state["pan_x"], state["pan_y"])

    def change_zoom(zoom_type):
        """Быстрое масштабирование сетки ЧПУ кнопками [+] и [-] на джойстике"""
        if zoom_type == "in": state["scale"] += 10.0
        elif zoom_type == "out": state["scale"] = max(10.0, state["scale"] - 10.0)
        
        # Обновляем текст плашки масштаба в реальном времени
        lbl_scale_text.config(text=f"Зум: {int(state['scale'])}%")
        editor_engine.scale_all_drawn_elements_engine(canvas, scale_pct=state["scale"])

    # Сохраняем функцию зума в объекте canvas, чтобы модуль мыши мог вызывать её при прокрутке колесиком
    canvas.trigger_mouse_zoom_callback = change_zoom

    # Сдвигаем всю сетку кнопок на один ряд вниз (row+1), освобождая место под плашку
    btn_up = create_joystick_button(joystick_frame, "arrow_up.png", "↑", lambda: move_panorama("up"))
    btn_up.grid(row=1, column=1, padx=1, pady=1)

    btn_plus = create_joystick_button(joystick_frame, "zoom_in.png", "+", lambda: change_zoom("in"))
    btn_plus.grid(row=1, column=2, padx=1, pady=1)

    btn_left = create_joystick_button(joystick_frame, "arrow_left.png", "←", lambda: move_panorama("left"))
    btn_left.grid(row=2, column=0, padx=1, pady=1)

    btn_center = create_joystick_button(joystick_frame, "center.png", "⛶", lambda: move_panorama("center"))
    btn_center.grid(row=2, column=1, padx=1, pady=1)

    btn_right = create_joystick_button(joystick_frame, "arrow_right.png", "→", lambda: move_panorama("right"))
    btn_right.grid(row=2, column=2, padx=1, pady=1)

    btn_down = create_joystick_button(joystick_frame, "arrow_down.png", "↓", lambda: move_panorama("down"))
    btn_down.grid(row=3, column=1, padx=1, pady=1)

    btn_minus = create_joystick_button(joystick_frame, "zoom_out.png", "-", lambda: change_zoom("out"))
    btn_minus.grid(row=3, column=2, padx=1, pady=1)

    def reposition_joystick_event(event):
        canvas.coords("joystick_window", event.width - 20, event.height - 20)
        canvas.tag_raise("joystick_window")
        
    canvas.bind("<Configure>", reposition_joystick_event)
