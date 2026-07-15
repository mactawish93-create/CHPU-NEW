import tkinter as tk
from tkinter import ttk
import base64

def load_interface(params_frame, canvas, controller):
    """
    Генерирует полную оригинальную параметрию диска 'Бабочка':
    геометрия, послойные шаги ЧПУ, подачи и параметры паза.
    """
    # Полностью очищаем холст и панели от старых элементов
    for widget in canvas.winfo_children():
        widget.destroy()
    for widget in params_frame.winfo_children():
        widget.destroy()

    type_var = tk.StringVar(value="Глухой")          
    size_var = tk.StringVar(value="2000")            
    door_offset_var = tk.StringVar(value="0 мм")      
    
    # Переключатель: Вырезать вертикальный паз под лаги?
    cut_paz_var = tk.StringVar(value="Да")

    # Создаем прокручиваемую область (Scrollbar), так как параметров очень много!
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

    # --- 1. КНОПКИ ВЫБОРА ТИПА ДИСКА ---
    type_frame = ttk.Frame(scrollable_frame, padding=2)
    type_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5, padx=5)
    
    btn_solid = tk.Button(type_frame, text="Глухой", font=("Arial", 9, "bold"), bg="#4a90e2", fg="white", bd=1, relief=tk.RAISED, width=11)
    btn_door = tk.Button(type_frame, text="С проемом", font=("Arial", 9), bg="#eaeaea", fg="black", bd=1, relief=tk.FLAT, width=11)
    btn_solid.pack(side=tk.LEFT, padx=1)
    btn_door.pack(side=tk.LEFT, padx=1)

    entries = {}

    # Вспомогательная функция для генерации компактных полей ввода ЧПУ (width=8)
    def create_row(parent, row, text, key, default_val):
        ttk.Label(parent, text=text).grid(row=row, column=0, sticky=tk.W, pady=2)
        ent = ttk.Entry(parent, width=8)
        ent.insert(0, default_val)
        ent.grid(row=row, column=1, padx=5, pady=2, sticky=tk.W)
        entries[key] = ent
        ent.bind("<KeyRelease>", lambda e: draw_preview(canvas, size_var, type_var, door_offset_var, cut_paz_var, entries))

    # --- 2. БЛОК ГЕОМЕТРИИ БАНИ-БОЧКИ ---
    geo_frame = ttk.LabelFrame(scrollable_frame, text=" Геометрия купола ", padding=8)
    geo_frame.grid(row=1, column=0, columnspan=2, fill=tk.X, padx=5, pady=4)

    ttk.Label(geo_frame, text="Размер диска:").grid(row=0, column=0, sticky=tk.W, pady=2)
    combo_size = ttk.Combobox(geo_frame, values=["2000", "2150", "2300"], textvariable=size_var, state="readonly", width=8)
    combo_size.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
    combo_size.bind("<<ComboboxSelected>>", lambda e: draw_preview(canvas, size_var, type_var, door_offset_var, cut_paz_var, entries))

    create_row(geo_frame, 1, "Высота в коньке (X):", "h_kon", "2200.0")
    create_row(geo_frame, 2, "Высота до излома:", "h_izl", "1340.0")

    # --- 3. БЛОК ТЕХНОЛОГИИ ЧПУ СТАНКА ---
    cnc_frame = ttk.LabelFrame(scrollable_frame, text=" Технология ЧПУ ", padding=8)
    cnc_frame.grid(row=2, column=0, columnspan=2, fill=tk.X, padx=5, pady=4)

    create_row(cnc_frame, 0, "Диаметр фрезы (мм):", "frez", "11.2")
    create_row(cnc_frame, 1, "Финальный рез Z:", "z", "-45.0")
    create_row(cnc_frame, 2, "Шаг за проход Z:", "step", "4.5")
    create_row(cnc_frame, 3, "Скорость подачи F:", "feed", "2000")

    # --- 4. БЛОК ВЕРТИКАЛЬНОГО ТЕХНОЛОГИЧЕСКОГО ПАЗА ---
    paz_frame = ttk.LabelFrame(scrollable_frame, text=" Пазировка под лаги ", padding=8)
    paz_frame.grid(row=3, column=0, columnspan=2, fill=tk.X, padx=5, pady=4)

    ttk.Label(paz_frame, text="Вырезать паз?").grid(row=0, column=0, sticky=tk.W, pady=2)
    combo_paz = ttk.Combobox(paz_frame, values=["Да", "Нет"], textvariable=cut_paz_var, state="readonly", width=8)
    combo_paz.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
    combo_paz.bind("<<ComboboxSelected>>", lambda e: draw_preview(canvas, size_var, type_var, door_offset_var, cut_paz_var, entries))

    create_row(paz_frame, 1, "Размер комнаты (Y):", "room", "1200.0")
    create_row(paz_frame, 2, "Глубина паза Z:", "z_paz", "-20.0")

    # --- 5. БЛОК ДВЕРНОГО ПРОЕМА (Отображается по условию кнопки) ---
    door_frame = ttk.LabelFrame(scrollable_frame, text=" Дверной проем ", padding=8)
    
    def update_door_ui():
        if type_var.get() == "С проемом":
            door_frame.grid(row=4, column=0, columnspan=2, fill=tk.X, padx=5, pady=4)
            # Если полей проема еще нет в подблоке - создаем их один раз
            if "offset" not in door_frame.winfo_children():
                ttk.Label(door_frame, text="Смещение двери:").grid(row=0, column=0, sticky=tk.W, pady=2)
                combo_offset = ttk.Combobox(door_frame, values=["0 мм", "100 мм", "150 мм"], textvariable=door_offset_var, state="readonly", width=8)
                combo_offset.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
                combo_offset.bind("<<ComboboxSelected>>", lambda e: draw_preview(canvas, size_var, type_var, door_offset_var, cut_paz_var, entries))
        else:
            door_frame.grid_forget()

    def set_disk_type(selected_type):
        type_var.set(selected_type)
        if selected_type == "Глухой":
            btn_solid.config(bg="#4a90e2", fg="white", relief=tk.RAISED, font=("Arial", 9, "bold"))
            btn_door.config(bg="#eaeaea", fg="black", relief=tk.FLAT, font=("Arial", 9))
        else:
            btn_solid.config(bg="#eaeaea", fg="black", relief=tk.FLAT, font=("Arial", 9))
            btn_door.config(bg="#4a90e2", fg="white", relief=tk.RAISED, font=("Arial", 9, "bold"))
        update_door_ui()
        draw_preview(canvas, size_var, type_var, door_offset_var, cut_paz_var, entries)

    btn_solid.config(command=lambda: set_disk_type("Глухой"))
    btn_door.config(command=lambda: set_disk_type("С проемом"))

    # Сохраняем все ссылки в контроллер ядра ЧПУ
    controller.active_inputs = entries
    controller.active_inputs["size_var"] = size_var
    controller.active_inputs["type_var"] = type_var
    controller.active_inputs["door_offset_var"] = door_offset_var
    controller.active_inputs["cut_paz_var"] = cut_paz_var

    set_disk_type("Глухой")


# =========================================================================
# ВСТРОЕННЫЙ ШАБЛОН ТОЧЕК КУПОЛА БАБОЧКИ (Base64)
# =========================================================================
BABOCHKA_TEMPLATE_DATA = 'LTYuMDAwLDE5MzQuOTIwDQotNi4wMDAsMzAyOS40ODkNCi01LjU0OSwzMDUxLjc0Nw0KLTQuNDk2LDMwNzMuOTg5DQotMi44NDIsMzA5Ni4xOTENCi0wLjM1MCwzMTIwLjEwMw0KMi44NzgsMzE0My45NzMNCjYuODQxLDMxNjcuNzY2DQoxMS41MzgsMzE5MS40NDkNCjE2Ljk2MSwzMjE0Ljk4Nw0KMjMuMTA2LDMyMzguMzQ4DQoyOS45NjEsMzI2MS40OTgNCjM3LjUxNiwzMjg0LjQwNQ0KNDUuNzU4LDMzMDcuMDM4DQo1NC42NzIsMzMyOS4zNjYNCjY0LjQwNiwzMzUxLjY4NQ0KNzQuODU1LDMzNzMuNzYyDQo4Ni4wMDksMzM5NS41NjQNCjk3Ljg1NywzNDE3LjA1OA0KMTEwLjM4NiwzNDM4LjIwOQ0KMTIzLjU4MSwzNDU4Ljk4Ng0KMTM3LjQyNiwzNDc5LjM1OQ0KMTUxLjkwMCwzNDk5LjI5Ng0KMTY2Ljk4MywzNTE4Ljc3MA0KMTgyLjY1MiwzNTM3Ljc1MQ0KMTk4Ljg4MywzNTU2LjIxNg0KMjE1LjY0OSwzNTc0LjEzOA0KMjMyLjkyNSwzNTkxLjQ5Ng0KMjUwLjY4MSwzNjA4LjI2OA0KMjY4Ljg4NywzNjI0LjQzNg0KMjg3LjcwNSwzNjQwLjE2OQ0KMzA3LjA2NCwzNjU1LjM1Nw0KMzI2Ljk0MiwzNjY5Ljk3Mg0KMzQ3LjMxMywzNjgzLjk4OA0KMzY4LjE1MCwzNjk3LjM4Mg0KMzg5LjQyNCwzNzEwLjEzMQ0KNDExLjEwMywzNzIyLjIxMw0KNDMzLjE1OCwzNzMzLjYxMA0KNDU1LjU1NSwzNzQ0LjMwNQ0KNDc4LjI2MCwzNzU0LjI4Mw0KNTAxLjIzOSwzNzYzLjUzMg0KNTI0LjQ1NiwzNzcyLjA0MA0KNTQ3Ljg3NywzNzc5LjgwMA0KNTcxLjQ2NSwzNzg2LjgwNg0KNTk1LjE4MywzNzkzLjA1NA0KNjExLjg4MCwzNzk2Ljk5NA0KNjI4LjY2OCwzODAwLjUzNQ0KNjQ1LjUzNCwzODAzLjY3Mw0KNzI5LjIyOSwzODE4LjI5Ng0KNzc3LjIzMSwzODI1Ljk4Mg0KODI1LjMxMywzODMzLjE1NA0KODc5LjAwOSwzODQwLjU5MA0KOTMyLjgxOSwzODQ3LjMyMg0KOTg2LjcyOCwzODUzLjM0OQ0KMTA0MC43MjQsMzg1OC42NjcNCjEwOTQuNzkyLDM4NjMuMjc2DQoxMTQ4LjkxOSwzODY3LjE3NA0KMTIwMy4wOTAsMzg3MC4zNTkNCjEyNTcuMjkxLDM4NzIuODMyDQoxMzExLjUwNywzODc0LjU5MQ0KMTM2NS43MjcsMzg3NS42MzgNCjE0MTkuOTM0LDM4NzUuOTcxDQoxNDM3LjIyNCwzODc1LjUyMw0KMTQ1NC42ODMsMzg3NC4zNTkNCjE0NzIuMjY5LDM4NzIuNDU4DQoxNDg5LjkzOCwzODY5LjgwMg0KMTUwNy42NDIsMzg2Ni4zNzYNCjE1MjUuMzMyLDM4NjIuMTY5DQoxNTQyLjk1OSwzODU3LjE3NQ0KMTU2MC40NzEsMzg1MS4zOTENCjE1NzcuODE1LDM4NDQuODE5DQoxNTk0LjkzOSwzODM3LjQ2NA0KMTYxMS43OTAsMzgyOS4zMzkNCjE2MjguMzE4LDM4MjAuNDU5DQoxNjQ0LjQ3MSwzODEwLjg0Mw0KMTY2MC4yMDEsMzgwMC41MTgNCjE2NzUuNDYyLDM3ODkuNTExDQoxNjkwLjIxMSwzNzc3Ljg1Ng0KMTcwNC40MDcsMzc2NS41ODkNCjE3MTguMDE0LDM3NTIuNzUwDQoxNzMwLjk5OCwzNzM5LjM4MQ0KMTc0My4zMzAsMzcyNS41MjcNCjE3NTQuOTg2LDM3MTEuMjM1DQoxNzY1Ljk0NCwzNjk2LjU1Mw0KMTc3Ni4xOTAsMzY4MS41MzANCjE3ODUuNzExLDM2NjYuMjE2DQoxNzk0LjUwMSwzNjUwLjY2MQ0KMTgwMi41NTYsMzYzNC45MTMNCjE4MDkuODc3LDM2MTkuMDIwDQoxODE2LjQ3MCwzNjAzLjAzMA0KMTgzNi43MzQsMzU1NC42ODgNCjE4NTYuNDAxLDM1MDYuMDg3DQoxODc1LjQ2NywzNDU3LjIzOQ0KMTg5My45MjcsMzQwOC4xNTQNCjE5MTEuNzc3LDMzNTguODQ0DQoxOTI5LjAxMywzMzA5LjMyMQ0KMTk0NS42MzEsMzI1OS41OTUNCjE5NjEuNjI3LDMyMDkuNjc4DQoxOTc4LjAxMSwzMTU2LjA4OQ0KMTk5My43MDIsMzEwMi4yMzgNCjIwMDguNjk1LDMwNDguMTM3DQoyMDIyLjk4NSwyOTkzLjgwMQ0KMjAzNi41NjYsMjkzOS4yNDINCjIwNDkuNDMzLDI4ODQuNDc2DQoyMDYxLjU4MSwyODI5LjUxNQ0KMjA3My4wMDcsMjc3NC4zNzQNCjIwODMuNzA2LDI3MTkuMDY4DQoyMDkzLjY3NSwyNjYzLjYxMA0KMjEwMi45MTEsMjYwOC4wMTYNCjIxMTEuNDExLDI1NTIuMjk5DQoyMTE5LjE3MywyNDk2LjQ3NQ0KMjEyNi4xOTQsMjQ0MC41NTgNCjIxMzIuNDc0LDIzODQuNTYyDQoyMTM4LjAxMSwyMzI4LjUwNA0KMjE0Mi44MDUsMjI3Mi4zOTYNCjIxNDYuODU0LDIyMTYuMjU1DQoyMTUwLjE1OSwyMTYwLjA5NA0KMjE1Mi43MjEsMjEwMy45MjkNCjIxNTQuNTQwLDIwNDcuNzc0DQoyMTU1LjYxNywxOTkxLjY0NQ0KMjE1NS45NTQsMTkzNS41NTUNCjIxNTUuNTUzLDE4NzkuNTE5DQoyMTU0LjQ2MCwxODIyLjA1NA0KMjE1Mi41OTAsMTc2NC41NzMNCjIxNDkuOTQ0LDE3MDcuMDkxDQoyMTQ2LjUyMSwxNjQ5LjYyMw0KMjE0Mi4zMjAsMTU5Mi4xODYNCjIxMzcuMzQzLDE1MzQuNzk2DQoyMTMxLjU4OSwxNDc3LjQ2Nw0KMjEyNS4wNjEsMTQyMC4yMTYNCjIxMTcuNzYwLDEzNjMuMDU4DQoyMTA5LjY4OCwxMzA2LjAxMA0KMjEwMC44NDcsMTI0OS4wODYNCjIwOTEuMjQxLDExOTIuMzAzDQoyMDgwLjg3MywxMTM1LjY3NA0KMjA2OS43NDcsMTA3OS4yMTcNCjIwNTcuODY2LDEwMjIuOTQ2DQoyMDQ1LjIzNiw5NjYuODc2DQoyMDMxLjY3Myw5MTAuNjE5DQoyMDE3LjM0Niw4NTQuNTIxDQoyMDAyLjI1OCw3OTguNTk4DQoxOTg2LjQxMyw3NDIuODY3DQoxOTY5LjgxNSw2ODcuMzQxDQoxOTUyLjQ2Niw2MzIuMDM2DQoxOTM0LjM3Myw1NzYuOTY5DQoxOTE1LjU0MCw1MjIuMTUyDQoxODk1Ljk3MSw0NjcuNjAyDQoxODc1LjY3NCw0MTMuMzMzDQoxODU0LjY1NCwzNTkuMzYwDQoxODMyLjkxNywzMDUuNjk3DQoxODEwLjQ3MCwyNTIuMzU4DQoxODAzLjE5MiwyMzYuNDE4DQoxNzk1LjE3MywyMjAuNjEyDQoxNzg2LjQxMSwyMDQuOTg5DQoxNzc2LjkwOCwxODkuNTk3DQoxNzY2LjY2OSwxNzQuNDg5DQoxNzU1LjcwNiwxNTkuNzEzDQoxNzQ0LjAzMiwxNDUuMzIyDQoxNzMxLjY2NywxMzEuMzYzDQoxNzE4LjYzNiwxMTcuODg2DQoxNzA0Ljk2NywxMDQuOTM3DQoxNjkwLjY5Miw5Mi41NjENCjE2NzUuODQ3LDgwLjc5OA0KMTY2MC40NzUsNjkuNjg3DQoxNjQ0LjYxNyw1OS4yNjMNCjE2MjguMzIyLDQ5LjU1Nw0KMTYxMS42MzcsNDAuNTk0DQoxNTk0LjYxNSwzMi4zOTcNCjE1NzcuMzA3LDI0Ljk4Mw0KMTU1OS43NjcsMTguMzY0DQoxNTQyLjA1MCwxMi41NDgNCjE1MjQuMjA5LDcuNTM4DQoxNTA2LjI5OCwzLjMzMg0KMTQ4OC4zNjgsLTAuMDc2DQoxNDcwLjQ3MCwtMi42OTcNCjE0NTIuNjUzLC00LjU0Ng0KMTQzNC45NjMsLTUuNjQwDQoxNDE3LjQ0NCwtNi4wMDANCjEzNjYuOTE0LC01LjcwNg0KMTMxNi4zODcsLTQuNzc4DQoxMjY1Ljg3NiwtMy4yMTgNCjEyMTUuMzkzLC0xLjAyNQ0KMTE2MS4zNjUsMi4wODcNCjExMDcuMzYxLDUuODc1DQoxMDUzLjM5MywxMC4zNDENCjk5OS40NzYsMTUuNDgyDQo5NDUuNjIwLDIxLjI5OQ0KODkxLjg0MCwyNy43OTENCjgzOC4xNDcsMzQuOTU1DQo3ODQuNTU0LDQyLjc4OQ0KNzMxLjA3NCw1MS4yOTMNCjY3Ny43MjAsNjAuNDYyDQo2MjQuNTAzLDcwLjI5NQ0KNjAwLjEyOCw3NS43MzMNCjU3NS45MDIsODEuOTUyDQo1NTEuODYxLDg4Ljk0NA0KNTI4LjA0Miw5Ni43MDANCjUwNC40ODIsMTA1LjIxMQ0KNDgxLjIxNywxMTQuNDYxDQo0NTguMjgwLDEyNC40MzYNCjQzNS43MDYsMTM1LjExOA0KNDE0LjA3MiwxNDYuMjExDQozOTIuNzIzLDE1Ny45OTgNCjM3MS42OTIsMTcwLjQ2OA0KMzUxLjAxMCwxODMuNjA5DQozMzAuNzEwLDE5Ny40MDYNCjMxMC44MjIsMjExLjg0MQ0KMjUzLjkyNywyNTguNzc3DQoyMzUuOTc1LDI3NS41NTgNCjIxOC41NzEsMjkyLjg2NQ0KMjAxLjczOCwzMTAuNjcxDQoxODUuNDk3LDMyOC45NDkNCjE2OS44NjYsMzQ3LjY2OA0KMTU0Ljg2MywzNjYuNzk5DQoxNDAuMjQ4LDM4Ni42MzkNCjEyNi4yMTYsNDA2Ljk5Mw0KMTEyLjc5NSw0MjcuODM2DQoxMDAuMDA4LDQ0OS4xMzgNCjg3Ljg4MCw0NzAuODcyDQo3Ni40MzAsNDkzLjAwNw0KNjUuNjc5LDUxNS41MTANCjU1LjY0Myw1MzguMzQ3DQo0Ni4zMzksNTYxLjQ4NQ0KMzcuNzc3LDU4NC44ODkNCjI5Ljk3MCw2MDguNTIyDQoyMi45MjYsNjMyLjM0OA0KMTYuNjUwLDY1Ni4zMzENCjExLjE0Niw2ODAuNDMyDQo2LjQxNiw3MDQuNjE2DQoyLjczNiw3MjcuMDczDQotMC4zMDUsNzQ5LjY0NA0KLTIuNzAyLDc3Mi4zMDINCi00LjQ1MSw3OTUuMDE5DQotNS41NTAsODE3Ljc2OA0KLTYuMDAwLDg0MC41MjA=' # Вставьте сюда базовую строку (base64)

def get_template_points():
    """Декодирует опорные точки купола"""
    # [Функция декодирования]
    pass

def draw_preview(canvas, size_var, type_var, door_offset_var, cut_paz_var, entries):
    """
    Инженерная отрисовка: вертикальные ламели, динамический паз.
    """
    canvas.delete("all")
    # [Логика масштабирования и отрисовки]

    # Визуализация технологического паза
    if cut_paz_var.get() == "Да":
        # [Расчет точки X_end_paz]
        pass
    # [Отрисовка осей]

def generate_gcode(inputs):
    """Генерация УП ЧПУ: послойный съем и автоматический паз."""
    # [Логика генерации G-кода, использующая переменные из inputs]
    pass
