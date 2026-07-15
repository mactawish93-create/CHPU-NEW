import tkinter as tk

# =========================================================================
# 🎨 ЕДИНЫЙ ПАСПОРТ СТИЛЯ ДЛЯ ВСЕХ ДИСКОВ БАНЬ-БОЧЕК
# =========================================================================
COLOR_WOOD_LIGHT = "#e3be81"    # Цвет светлых ламелей доски
COLOR_WOOD_DARK  = "#dbb574"    # Цвет темных ламелей доски
COLOR_CONTOUR    = "#b38642"    # Наружный главный контур диска
COLOR_AXIS       = "#444444"    # Цвет стрелок осей ЧПУ
COLOR_DIM_LINE   = "#999999"    # Цвет размерных стрелок
COLOR_TEXT_MAIN  = "#333333"    # Цвет шрифта размеров

FONT_DIM_BOLD    = ("Arial", 10, "bold")
FONT_SMALL_BLUE  = ("Arial", 8, "bold")

def get_safe_size(canvas):
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    return (800 if w < 100 else w, 450 if h < 100 else h)

def draw_disk_axes(canvas, w_width, w_height, cx, cy, r_px):
    """Чертит тонкие перекрестия по центру диска и ИСПРАВЛЕННЫЕ стрелки станка в углу"""
    canvas.create_line(cx - r_px - 20, cy, cx + r_px + 20, cy, fill=COLOR_DIM_LINE, dash=(4,2))
    canvas.create_line(cx, cy - r_px - 20, cx, cy + r_px + 20, fill=COLOR_DIM_LINE, dash=(4,2))

    # 🚀 ИСПРАВЛЕНИЕ ОСЕЙ: По вашему ТЗ для дисков: X идет горизонтально вправо, Y идет вертикально вверх!
    axis_x0, axis_y0 = 40, w_height - 50
    # Ось Y станка идет вертикально вверх (вдоль ламелей)
    canvas.create_line(axis_x0, axis_y0, axis_x0, axis_y0 - 45, fill=COLOR_AXIS, arrow=tk.LAST, width=2)
    canvas.create_text(axis_x0 - 12, axis_y0 - 40, text="Y", font=("Arial", 10, "bold"), fill=COLOR_AXIS)
    # Ось X станка идет горизонтально вправо (поперек ламелей)
    canvas.create_line(axis_x0, axis_y0, axis_x0 + 45, axis_y0, fill=COLOR_AXIS, arrow=tk.LAST, width=2)
    canvas.create_text(axis_x0 + 40, axis_y0 + 12, text="X", font=("Arial", 10, "bold"), fill=COLOR_AXIS)
    canvas.create_text(axis_x0 - 10, axis_y0 + 10, text="0", font=("Arial", 8, "bold"), fill=COLOR_AXIS)

def get_door_geometry(size_mm, offset_text):
    """Возвращает точные технологические параметры проема на основе заводских G-кодов"""
    door_w = 752.0
    door_h = 1772.0
    
    # Смещение по оси X (горизонтальное — влево по заготовке)
    offset_x = 0.0
    if "100" in offset_text: offset_x = -100.0
    elif "150" in offset_text: offset_x = -150.0
    
    # Смещение по оси Y (вертикальное — вниз по заготовке)
    offset_y = 0.0
    if int(size_mm) == 2000 and "100" in offset_text:
        door_h = 1672.0  # Для 2000-100 проем ниже на 100 мм
    elif int(size_mm) == 2300:
        offset_y = -104.0 # Для 2300 проем всегда сдвинут вниз на 104 мм
        
    return door_w, door_h, offset_x, offset_y


# =========================================================================
# 🔵 ФУНКЦИЯ 1: МАКСИМАЛЬНЫЙ КРУГЛЫЙ ДИСК С ДВУСТОРОННЕЙ ГРЕБЕНКОЙ И ПИКОВОЙ ТОЧКОЙ
# =========================================================================
def draw_round_disk_preview(canvas, size_var, type_var, door_offset_var):
    canvas.delete("all")
    w_width, w_height = get_safe_size(canvas)
    
    try: dia = float(size_var.get())
    except ValueError: dia = 2000.0

    # 🚀 МАКСИМАЛЬНЫЙ МАСШТАБ: рассчитываем строго от высоты холста
    scale = (w_height - 180) / max(dia, 500.0)
    cx, cy = w_width / 2, w_height / 2
    r_px = (dia / 2.0) * scale
    
    canvas.create_oval(cx - r_px, cy - r_px, cx + r_px, cy + r_px, fill="#ffffff", outline="")

    has_door = (type_var.get() == "С проемом")
    dr_w, dr_h, dr_ox, dr_oy = get_door_geometry(dia, door_offset_var.get())

    # Шаг ламелей по 140 мм
    board_w_mm = 140.0
    board_w_px = board_w_mm * scale
    start_x_px, end_x_px = cx - r_px, cx + r_px
    current_x, board_idx = start_x_px, 0

    while current_x < end_x_px:
        next_x = min(current_x + board_w_px, end_x_px)
        mid_x_px = (current_x + next_x) / 2
        dx_center = mid_x_px - cx
        
        if abs(dx_center) < r_px:
            # Считаем края ламели в мм от центра, чтобы найти истинный геометрический пик
            mm_left_edge = (current_x - cx) / scale
            mm_right_edge = (next_x - cx) / scale
            # 🚀 НАХОДИМ ПИКОВУЮ (СИНЮЮ) ТОЧКУ: та координата, что ближе к центру по оси X, даст максимум высоты по Y
            mm_x_critical = mm_left_edge if abs(mm_left_edge) < abs(mm_right_edge) else mm_right_edge
            
            # Точный расчет чистой длины доски по пиковой точке
            full_len_mm = int(2 * ((dia/2.0)**2 - mm_x_critical**2)**0.5)
            
            # Вычисляем истинную графическую высоту прямоугольника на экране по пику (чтобы правый угол не торчал!)
            dy_px_visual = ((r_px)**2 - (mm_x_critical * scale)**2) ** 0.5
            
            b_color = COLOR_WOOD_LIGHT if board_idx % 2 == 0 else COLOR_WOOD_DARK
            canvas.create_rectangle(current_x, cy - dy_px_visual, next_x, cy + dy_px_visual, fill=b_color, outline="#cc9e52", width=1)
            
            # Защита от выноса микро-обрубков краев
            if full_len_mm > 150:
                mm_mid_x = dx_center / scale
                in_door_zone = has_door and ((dr_ox - dr_w/2.0) <= mm_mid_x <= (dr_ox + dr_w/2.0))
                
                # 🚀 ДВУСТОРОННЯЯ ГРЕБЕНКА: четные доски шагают ВВЕРХ, нечетные — ВНИЗ!
                if board_idx % 2 == 0:
                    shelf_y = cy - r_px - 35
                    canvas.create_line(mid_x_px, cy - dy_px_visual, mid_x_px, shelf_y, fill="#cccccc", dash=(2,2))
                    canvas.create_line(mid_x_px, shelf_y, mid_x_px + 8, shelf_y, fill=COLOR_DIM_LINE)
                    
                    if in_door_zone:
                        bottom_mm = int(max(0, (full_len_mm/2.0) + dr_oy - dr_h/2.0))
                        top_mm = int(max(0, (full_len_mm/2.0) - dr_oy - dr_h/2.0))
                        canvas.create_text(mid_x_px + 4, shelf_y - 10, text=str(full_len_mm), font=FONT_DIM_BOLD, fill=COLOR_TEXT_MAIN, anchor=tk.W)
                        canvas.create_text(mid_x_px + 4, shelf_y + 8, text=f"{top_mm}/{bottom_mm}", font=FONT_SMALL_BLUE, fill="#1d4182", anchor=tk.W)
                    else:
                        canvas.create_text(mid_x_px + 4, shelf_y - 5, text=str(full_len_mm), font=FONT_DIM_BOLD, fill=COLOR_TEXT_MAIN, anchor=tk.W)
                else:
                    shelf_y = cy + r_px + 35
                    canvas.create_line(mid_x_px, cy + dy_px_visual, mid_x_px, shelf_y, fill="#cccccc", dash=(2,2))
                    canvas.create_line(mid_x_px, shelf_y, mid_x_px + 8, shelf_y, fill=COLOR_DIM_LINE)
                    
                    if in_door_zone:
                        bottom_mm = int(max(0, (full_len_mm/2.0) + dr_oy - dr_h/2.0))
                        top_mm = int(max(0, (full_len_mm/2.0) - dr_oy - dr_h/2.0))
                        canvas.create_text(mid_x_px + 4, shelf_y - 10, text=str(full_len_mm), font=FONT_DIM_BOLD, fill=COLOR_TEXT_MAIN, anchor=tk.W)
                        canvas.create_text(mid_x_px + 4, shelf_y + 8, text=f"{top_mm}/{bottom_mm}", font=FONT_SMALL_BLUE, fill="#1d4182", anchor=tk.W)
                    else:
                        canvas.create_text(mid_x_px + 4, shelf_y - 5, text=str(full_len_mm), font=FONT_DIM_BOLD, fill=COLOR_TEXT_MAIN, anchor=tk.W)

        current_x, board_idx = next_x, board_idx + 1

    canvas.create_oval(cx - r_px, cy - r_px, cx + r_px, cy + r_px, fill="", outline=COLOR_CONTOUR, width=2)

    # Отрисовка проема двери со ступенькой-четвертью 22 мм
    if has_door:
        dx1 = cx + (dr_ox - dr_w/2.0) * scale
        dx2 = cx + (dr_ox + dr_w/2.0) * scale
        dy1 = cy - (dr_oy + dr_h/2.0) * scale
        dy2 = cy - (dr_oy - dr_h/2.0) * scale
        
        dx_inner1 = dx1 + 22.0 * scale
        dx_inner2 = dx2 - 22.0 * scale
        dy_inner1 = dy1 + 20.0 * scale
        dy_inner2 = dy2 - 20.0 * scale
        
        canvas.create_rectangle(dx1, dy1, dx2, dy2, fill="#ffffff", outline="#ff4444", width=1, dash=(3,2))
        canvas.create_rectangle(dx_inner1, dy_inner1, dx_inner2, dy_inner2, fill="#ffffff", outline="#ff4444", width=1)
        canvas.create_text(cx + dr_ox*scale, (dy1+dy2)/2, text="ПРОЕМ ДВЕРИ", font=("Arial", 9, "bold"), fill="#ff4444")

    # Общая чертежная выноска диаметра
    canvas.create_text(cx, cy - r_px - 15, text=f"Ø {int(dia)}", font=("Arial", 11, "bold"), fill=COLOR_TEXT_MAIN)
    canvas.create_line(cx - r_px, cy - r_px - 5, cx + r_px, cy - r_px - 5, fill=COLOR_DIM_LINE, arrow=tk.BOTH)

    draw_disk_axes(canvas, w_width, w_height, cx, cy, r_px)


# =========================================================================
# 🟩 ФУНКЦИЯ 2: МАКСИМАЛЬНЫЙ КВАДРО ДИСК С ДВУСТОРОННЕЙ ГРЕБЕНКОЙ И ПИКОВОЙ ТОЧКОЙ
# =========================================================================
def draw_quadro_disk_preview(canvas, size_var, type_var, door_offset_var):
    canvas.delete("all")
    w_width, w_height = get_safe_size(canvas)
    
    try: size_mm = float(size_var.get())
    except ValueError: size_mm = 2000.0

    # 🚀 МАКСИМАЛЬНЫЙ МАСШТАБ
    scale = (w_height - 180) / max(size_mm, 500.0)
    cx, cy = w_width / 2, w_height / 2
    half_px = (size_mm / 2.0) * scale
    
    # Заводской радиус скругления углов Квадро-бочки (350 мм)
    r_corner_mm = 350.0
    r_corner_px = r_corner_mm * scale 

    x1, y1 = cx - half_px, cy - half_px
    x2, y2 = cx + half_px, cy + half_px

    canvas.create_rectangle(x1, y1, x2, y2, fill="#ffffff", outline="")

    has_door = (type_var.get() == "С проемом")
    dr_w, dr_h, dr_ox, dr_oy = get_door_geometry(size_mm, door_offset_var.get())

    # Шаг вертикальных ламелей по 140 мм
    board_w_mm = 140.0
    board_w_px = board_w_mm * scale
    current_x, board_idx = x1, 0
    
    while current_x < x2:
        next_x = min(current_x + board_w_px, x2)
        mid_x_px = (current_x + next_x) / 2
        dx_center = mid_x_px - cx
        
        # --- 🚀 УМНЫЙ РАСЧЕТ ДЛИНЫ КВАДРО-ДОСКИ ПО ПИКОВОЙ ТОЧКЕ ---
        mm_left_edge = (current_x - cx) / scale
        mm_right_edge = (next_x - cx) / scale
        mm_x_critical = mm_left_edge if abs(mm_left_edge) < abs(mm_right_edge) else mm_right_edge
        
        full_len_mm = size_mm
        dist_to_edge_mm = (size_mm / 2.0) - abs(mm_x_critical)
        
        if dist_to_edge_mm < r_corner_mm:
            y_corner_mm = r_corner_mm - (r_corner_mm**2 - (r_corner_mm - dist_to_edge_mm)**2)**0.5
            full_len_mm = size_mm - (2 * y_corner_mm)
            
        full_len_mm = int(full_len_mm)
        
        # Вычисляем истинные визуальные границы доски на экране
        top_edge_y = y1
        bot_edge_y = y2
        if dist_to_edge_mm < r_corner_mm:
            offset_px = ((size_mm - full_len_mm)/2.0) * scale
            top_edge_y = y1 + offset_px
            bot_edge_y = y2 - offset_px

        b_color = COLOR_WOOD_LIGHT if board_idx % 2 == 0 else COLOR_WOOD_DARK
        canvas.create_rectangle(current_x, top_edge_y, next_x, bot_edge_y, fill=b_color, outline="#cc9e52", width=1)
        
        if full_len_mm > 150:
            mm_mid_x = dx_center / scale
            in_door_zone = has_door and ((dr_ox - dr_w/2.0) <= mm_mid_x <= (dr_ox + dr_w/2.0))
            
            # 🚀 ДВУСТОРОННЯЯ ГРЕБЕНКА ДЛЯ КВАДРО-ДИСКА
            if board_idx % 2 == 0:
                shelf_y = y1 - 35
                canvas.create_line(mid_x_px, top_edge_y, mid_x_px, shelf_y, fill="#cccccc", dash=(2,2))
                canvas.create_line(mid_x_px, shelf_y, mid_x_px + 8, shelf_y, fill=COLOR_DIM_LINE)
                
                if in_door_zone:
                    bottom_mm = int(max(0, (full_len_mm/2.0) + dr_oy - dr_h/2.0))
                    top_mm = int(max(0, (full_len_mm/2.0) - dr_oy - dr_h/2.0))
                    canvas.create_text(mid_x_px + 4, shelf_y - 10, text=str(full_len_mm), font=FONT_DIM_BOLD, fill=COLOR_TEXT_MAIN, anchor=tk.W)
                    canvas.create_text(mid_x_px + 4, shelf_y + 8, text=f"{top_mm}/{bottom_mm}", font=FONT_SMALL_BLUE, fill="#1d4182", anchor=tk.W)
                else:
                    canvas.create_text(mid_x_px + 4, shelf_y - 5, text=str(full_len_mm), font=FONT_DIM_BOLD, fill=COLOR_TEXT_MAIN, anchor=tk.W)
            else:
                shelf_y = y2 + 35
                canvas.create_line(mid_x_px, bot_edge_y, mid_x_px, shelf_y, fill="#cccccc", dash=(2,2))
                canvas.create_line(mid_x_px, shelf_y, mid_x_px + 8, shelf_y, fill=COLOR_DIM_LINE)
                
                if in_door_zone:
                    bottom_mm = int(max(0, (full_len_mm/2.0) + dr_oy - dr_h/2.0))
                    top_mm = int(max(0, (full_len_mm/2.0) - dr_oy - dr_h/2.0))
                    canvas.create_text(mid_x_px + 4, shelf_y - 10, text=str(full_len_mm), font=FONT_DIM_BOLD, fill=COLOR_TEXT_MAIN, anchor=tk.W)
                    canvas.create_text(mid_x_px + 4, shelf_y + 8, text=f"{top_mm}/{bottom_mm}", font=FONT_SMALL_BLUE, fill="#1d4182", anchor=tk.W)
                else:
                    canvas.create_text(mid_x_px + 4, shelf_y - 5, text=str(full_len_mm), font=FONT_DIM_BOLD, fill=COLOR_TEXT_MAIN, anchor=tk.W)

        current_x, board_idx = next_x, board_idx + 1

    # Закрашиваем и скругляем внешние углы на заготовке Квадро фрезой ЧПУ
    canvas.create_rectangle(x1-2, y1-2, x1 + r_corner_px, y1 + r_corner_px, fill="#ffffff", outline="")
    canvas.create_arc(x1, y1, x1 + r_corner_px*2, y1 + r_corner_px*2, start=90, extent=90, fill=COLOR_WOOD_LIGHT, outline="#cc9e52")
    canvas.create_rectangle(x2 - r_corner_px, y1-2, x2+2, y1 + r_corner_px, fill="#ffffff", outline="")
    canvas.create_arc(x2 - r_corner_px*2, y1, x2, y1 + r_corner_px*2, start=0, extent=90, fill=COLOR_WOOD_DARK, outline="#cc9e52")
    canvas.create_rectangle(x1-2, y2 - r_corner_px, x1 + r_corner_px, y2+2, fill="#ffffff", outline="")
    canvas.create_arc(x1, y2 - r_corner_px*2, x1 + r_corner_px*2, y2, start=180, extent=90, fill=COLOR_WOOD_DARK, outline="#cc9e52")
    canvas.create_rectangle(x2 - r_corner_px, y2 - r_corner_px, x2+2, y2+2, fill="#ffffff", outline="")
    canvas.create_arc(x2 - r_corner_px*2, y2 - r_corner_px*2, x2, y2, start=270, extent=90, fill=COLOR_WOOD_LIGHT, outline="#cc9e52")

    # Чистовой Квадро-контур станка
    canvas.create_line(x1 + r_corner_px, y1, x2 - r_corner_px, y1, fill=COLOR_CONTOUR, width=2)
    canvas.create_line(x1 + r_corner_px, y2, x2 - r_corner_px, y2, fill=COLOR_CONTOUR, width=2)
    canvas.create_line(x1, y1 + r_corner_px, x1, y2 - r_corner_px, fill=COLOR_CONTOUR, width=2)
    canvas.create_line(x2, y1 + r_corner_px, x2, y2 - r_corner_px, fill=COLOR_CONTOUR, width=2)

    # Отрисовка проема двери со ступенькой-четвертью 22 мм
    if has_door:
        dx1 = cx + (dr_ox - dr_w/2.0) * scale
        dx2 = cx + (dr_ox + dr_w/2.0) * scale
        dy1 = cy - (dr_oy + dr_h/2.0) * scale
        dy2 = cy - (dr_oy - dr_h/2.0) * scale
        
        dx_inner1 = dx1 + 22.0 * scale
        dx_inner2 = dx2 - 22.0 * scale
        dy_inner1 = dy1 + 20.0 * scale
        dy_inner2 = dy2 - 20.0 * scale
        
        canvas.create_rectangle(dx1, dy1, dx2, dy2, fill="#ffffff", outline="#ff4444", width=1, dash=(3,2))
        canvas.create_rectangle(dx_inner1, dy_inner1, dx_inner2, dy_inner2, fill="#ffffff", outline="#ff4444", width=1)
        canvas.create_text(cx + dr_ox*scale, (dy1+dy2)/2, text="ПРОЕМ ДВЕРИ", font=("Arial", 9, "bold"), fill="#ff4444")

    # Чертежный размер сверху со знаком квадрата
    canvas.create_text(cx, y1 - 15, text=f"⌗ {int(size_mm)}", font=FONT_DIM_BOLD, fill=COLOR_TEXT_MAIN)
    canvas.create_line(x1, y1 - 5, x2, y1 - 5, fill=COLOR_DIM_LINE, arrow=tk.BOTH)

    draw_disk_axes(canvas, w_width, w_height, cx, cy, half_px)
