import tkinter as tk

# =========================================================================
# 🎨 ГЛОБАЛЬНЫЕ НАСТРОЙКИ СТИЛЯ БРЕНДА
# =========================================================================
COLOR_WOOD_LIGHT = "#e3be81"    # Цвет светлых ламелей доски
COLOR_WOOD_DARK  = "#dbb574"    # Цвет темных ламелей доски
COLOR_CONTOUR    = "#b38642"    # Главный контур фрезеровки заготовки
COLOR_AXIS       = "#444444"    # Цвет стрелок осей X / Y станка ЧПУ
COLOR_DIM_LINE   = "#999999"    # Цвет чертежных размерных стрелок
COLOR_TEXT_MAIN  = "#333333"    # Базовый цвет шрифта размеров
COLOR_SLOT_CNC   = "#9c702d"    # Цвет выборки пазов фрезой ЧПУ

FONT_DIM_BOLD    = ("Arial", 9, "bold")

def get_safe_canvas_size(canvas):
    """Безопасно считывает размеры холста с защитой от багов сжатия окон"""
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    return (800 if w < 100 else w, 450 if h < 100 else h)

def draw_axes_arrows(canvas, origin_x, origin_y, label_v, label_h):
    """Универсальная функция прорисовки стрелок системы координат станка"""
    # Вертикальная ось станка
    canvas.create_line(origin_x, origin_y, origin_x, origin_y - 45, fill=COLOR_AXIS, arrow=tk.LAST, width=2)
    canvas.create_text(origin_x - 12, origin_y - 40, text=label_v, font=("Arial", 10, "bold"), fill=COLOR_AXIS)
    # Горизонтальная ось станка
    canvas.create_line(origin_x, origin_y, origin_x + 45, origin_y, fill=COLOR_AXIS, arrow=tk.LAST, width=2)
    canvas.create_text(origin_x + 40, origin_y + 12, text=label_h, font=("Arial", 10, "bold"), fill=COLOR_AXIS)
    canvas.create_text(origin_x - 10, origin_y + 10, text="0", font=("Arial", 8, "bold"), fill=COLOR_AXIS)


# =========================================================================
# 🪵 РАЗДЕЛ 1: ОТРИСОВКА ЛЕЖЕК И ПАЗИРОВКИ БАНИ
# =========================================================================
def draw_paz_beam_engine(canvas, front_v, back_v, wood_x, slot_w, active_rooms, mode_text, total_slots):
    """Инженерная отрисовка набранного щита лежек с исправленной цепочкой стрелок"""
    canvas.delete("all")
    w_width, w_height = get_safe_canvas_size(canvas)

    if active_rooms:
        total_length = front_v + sum(active_rooms) + ((len(active_rooms) + 1) * slot_w) + back_v
    else:
        total_length = front_v + slot_w + back_v

    canvas.create_text(15, 10, text=f"Режим обработки: {mode_text.upper()}", font=("Arial", 10, "bold"), fill="#444444", anchor=tk.NW)
    canvas.create_text(15, 26, text=f"Пазов под диски: {total_slots} шт.", font=("Arial", 10), fill="#444444", anchor=tk.NW)

    scale_x = (w_width - 180) / total_length
    scale_y = (w_height - 180) / wood_x
    scale = min(scale_x, scale_y)

    start_x = 90 
    board_h = wood_x * scale
    board_w_px = total_length * scale
    board_y = 70 + (w_height - 180 - board_h) / 2 

    board_thickness_mm = 140.0
    num_boards = max(1, round(wood_x / board_thickness_mm))
    single_board_h = board_h / num_boards
    
    for b in range(num_boards):
        by1 = board_y + (b * single_board_h)
        by2 = by1 + single_board_h
        b_color = COLOR_WOOD_LIGHT if b % 2 == 0 else COLOR_WOOD_DARK
        canvas.create_rectangle(start_x, by1, start_x + board_w_px, by2, fill=b_color, outline="#cc9e52", width=1)
    
    canvas.create_rectangle(start_x, board_y, start_x + board_w_px, board_y + board_h, outline=COLOR_CONTOUR, width=2)
    
    canvas.create_line(start_x, board_y - 35, start_x, board_y + board_h + 10, fill="#ff4444", width=1, dash=(3,2))
    canvas.create_line(start_x + board_w_px, board_y - 35, start_x + board_w_px, board_y + board_h + 10, fill="#ff4444", width=1, dash=(3,2))

    segments = [{"val": front_v, "type": "front"}]
    if active_rooms:
        for r_len in active_rooms:
            segments.append({"val": slot_w, "type": "slot"})
            segments.append({"val": r_len, "type": "room"})
    segments.append({"val": slot_w, "type": "slot"})
    segments.append({"val": back_v, "type": "back"})

    curr_segment_x = start_x
    dim_line_y = board_y - 25 

    for idx, seg in enumerate(segments):
        seg_w_px = seg["val"] * scale
        next_segment_x = curr_segment_x + seg_w_px
        
        if seg["val"] > 0:
            canvas.create_line(curr_segment_x, dim_line_y, next_segment_x, dim_line_y, fill=COLOR_DIM_LINE, arrow=tk.BOTH)
            mid_x = curr_segment_x + seg_w_px / 2
            font_color = "#1d4182" if seg["type"] == "slot" else COLOR_TEXT_MAIN
            
            if seg["val"] < 100:
                text_y_offset = 12 if idx % 2 == 0 else -12
            else:
                text_y_offset = -12
                
            canvas.create_text(mid_x, dim_line_y + text_y_offset, text=str(int(seg["val"])), font=FONT_DIM_BOLD, fill=font_color)
            canvas.create_line(next_segment_x, dim_line_y - 5, next_segment_x, dim_line_y + 5, fill=COLOR_DIM_LINE)

        curr_segment_x = next_segment_x

    canvas.create_text(start_x - 40, board_y + board_h/2, text=f"{int(wood_x)}", font=FONT_DIM_BOLD, fill="#555555")
    canvas.create_line(start_x - 15, board_y, start_x - 15, board_y + board_h, fill=COLOR_DIM_LINE, arrow=tk.BOTH)

    canvas.create_text(start_x + board_w_px/2, board_y + board_h + 35, text=f"{int(total_length)}", font=("Arial", 13, "bold"), fill="#111111")
    canvas.create_line(start_x, board_y + board_h + 18, start_x + board_w_px, board_y + board_h + 18, fill=COLOR_DIM_LINE, arrow=tk.BOTH)

    current_slot_x = start_x + (front_v * scale)
    for r_len in (active_rooms if active_rooms else []):
        canvas.create_rectangle(current_slot_x, board_y, current_slot_x + (slot_w * scale), board_y + board_h, fill=COLOR_SLOT_CNC, outline="#664614", width=1)
        canvas.create_line(current_slot_x, board_y, current_slot_x, dim_line_y + 5, fill="#cccccc", dash=(2,2))
        canvas.create_line(current_slot_x + (slot_w * scale), board_y, current_slot_x + (slot_w * scale), dim_line_y + 5, fill="#cccccc", dash=(2,2))
        current_slot_x += (slot_w * scale) + (r_len * scale)
        
    canvas.create_rectangle(current_slot_x, board_y, current_slot_x + (slot_w * scale), board_y + board_h, fill=COLOR_SLOT_CNC, outline="#664614", width=1)
    canvas.create_line(current_slot_x, board_y, current_slot_x, dim_line_y + 5, fill="#cccccc", dash=(2,2))
    canvas.create_line(current_slot_x + (slot_w * scale), board_y, current_slot_x + (slot_w * scale), dim_line_y + 5, fill="#cccccc", dash=(2,2))

    draw_axes_arrows(canvas, 40, w_height - 50, "X", "Y")


# =========================================================================
# 🪵 РАЗДЕЛ 2: ОТРИСОВКА ПРОИЗВОЛЬНОЙ ПАЗИРОВКИ (СЖАТИЕ ВЫСОТЫ ПО L И T)
# =========================================================================
def draw_custom_paz_engine(canvas, valid_pazes, valid_torces):
    """
    Чертит заготовку, динамически сжимая её высоту по оси X под размеры L и T.
    Все ошибки с NameError полностью устранены!
    """
    canvas.delete("all")
    w_width, w_height = get_safe_canvas_size(canvas)

    # 1. ⚙️ ВОССТАНОВЛЕНО: Исправлен расчет максимальной длины по оси Y (горизонтально)
    max_length_mm = 1000.0  
    for paz in valid_pazes:
        if (paz["o"] + paz["w"]) > max_length_mm:
            max_length_mm = paz["o"] + paz["w"]
    for torc in valid_torces:
        if (torc["o"]) > max_length_mm:
            max_length_mm = torc["o"]

    # 2. ⚙️ РАСЧЕТ ВЫСОТЫ ПО X: Высота щита строго равна максимальной длине паза L или торца T
    max_height_mm = 0.0 
    for paz in valid_pazes:
        if paz["l"] > max_height_mm:
            max_height_mm = paz["l"]
    for torc in valid_torces:
        if torc["l"] > max_height_mm:
            max_height_mm = torc["l"]

    # Если оператор еще ничего не ввел, заложим аккуратный стартовый габарит 300 мм
    if max_height_mm == 0:
        max_height_mm = 300.0

    # Задаем общие габариты заготовки на экране ЧПУ
    total_beam_length = max_length_mm + 200.0  # Длина по Y (запас справа 200 мм)
    dynamic_wood_x = max_height_mm             # Высота по X строго по размеру L или T!

    # Вычисляем масштаб графики исходя из честных размеров
    scale_x = (w_width - 220) / total_beam_length
    scale_y = (w_height - 180) / dynamic_wood_x
    scale = min(scale_x, scale_y)

    start_x = 90
    board_h = dynamic_wood_x * scale  # Физическая высота бруса на экране в пикселях
    board_w_px = total_beam_length * scale
    board_y = 110 

    # Рисуем брус-заготовку (ламели по 140 мм укладываются строго в этот размер)
    num_boards = max(1, round(dynamic_wood_x / 140.0))
    single_board_h = board_h / num_boards
    for b in range(num_boards):
        by1 = board_y + (b * single_board_h)
        by2 = by1 + single_board_h
        b_color = COLOR_WOOD_LIGHT if b % 2 == 0 else COLOR_WOOD_DARK
        canvas.create_rectangle(start_x, by1, start_x + board_w_px, by2, fill=b_color, outline="#cc9e52", width=1)
    
    canvas.create_rectangle(start_x, board_y, start_x + board_w_px, board_y + board_h, outline=COLOR_CONTOUR, width=2)

    # Линия Базы станка (Абсолютный ноль оси Y)
    canvas.create_line(start_x, board_y - 35, start_x, board_y + board_h + 35, fill="#333333", width=2)
    canvas.create_text(start_x, board_y - 45, text="БАЗА Y=0", font=("Arial", 9, "bold"), fill="#1d4182")

    # --- 3. РАССТАВЛЯЕМ ВЕРТИКАЛЬНЫЕ ПАЗЫ (СНИЗУ ВВЕРХ ПО ФОТО) ---
    dim_line_y = board_y - 25

    for paz in valid_pazes:
        py1_px = start_x + (paz["o"] * scale)          
        py2_px = py1_px + (paz["w"] * scale)          
        
        px1_px = board_y + board_h                    
        px2_px = px1_px - (paz["l"] * scale)          

        if py2_px > py1_px and px1_px > px2_px:
            canvas.create_rectangle(py1_px, px2_px, py2_px, px1_px, fill=COLOR_SLOT_CNC, outline="#664614", width=1)
            
            canvas.create_line(py1_px, board_y, py1_px, dim_line_y - 5, fill="#cccccc", dash=(2,2))
            canvas.create_line(py2_px, board_y, py2_px, dim_line_y - 5, fill="#cccccc", dash=(2,2))
            
            canvas.create_line(py1_px, dim_line_y, py2_px, dim_line_y, fill=COLOR_DIM_LINE, arrow=tk.BOTH)
            canvas.create_text((py1_px + py2_px)/2, dim_line_y - 10, text=f"W {int(paz['w'])}", font=FONT_DIM_BOLD, fill="#1d4182")
            
            # Стрелка длины L строго внутри паза снизу вверх
            mid_y_px = (py1_px + py2_px) / 2
            canvas.create_line(mid_y_px, px1_px, mid_y_px, px2_px, fill="#888888", arrow=tk.BOTH, width=1)
            canvas.create_text(mid_y_px + 28, (px1_px + px2_px)/2, text=f"L {int(paz['l'])}", font=FONT_DIM_BOLD, fill="#333333")
            
            if paz["o"] > 0:
                canvas.create_line(start_x, board_y + board_h + 15, py1_px, board_y + board_h + 15, fill="#777777", arrow=tk.LAST)
                canvas.create_text((start_x + py1_px)/2, board_y + board_h + 25, text=f"От 0: {int(paz['o'])}", font=("Arial", 8, "bold"), fill="#555555")

    # --- 4. РАССТАВЛЯЕМ ПОПЕРЕЧНЫЕ ТОРЦЫ (СНИЗУ ВВЕРХ ПО ФОТО) ---
    for torc in valid_torces:
        ty_px = start_x + (torc["o"] * scale)
        tx1_px = board_y + board_h                     
        tx2_px = tx1_px - (torc["l"] * scale)          
        
        if tx1_px > tx2_px:
            canvas.create_rectangle(ty_px, tx2_px, ty_px + 10, tx1_px, fill="", outline="#ff3333", width=2, dash=(4,2))
            canvas.create_line(ty_px, tx2_px - 10, ty_px, tx1_px + 10, fill="#ff3333", width=2)
            
            canvas.create_line(ty_px - 15, tx1_px, ty_px - 15, tx2_px, fill="#ff3333", arrow=tk.BOTH)
            canvas.create_text(ty_px - 38, (tx1_px + tx2_px)/2, text=f"T {int(torc['l'])}", font=FONT_DIM_BOLD, fill="#ff3333")

            if torc["o"] > 0:
                canvas.create_line(start_x, board_y + board_h + 38, ty_px, board_y + board_h + 38, fill="#ff4444", arrow=tk.LAST)
                canvas.create_text((start_x + ty_px)/2, board_y + board_h + 48, text=f"Торц от 0: {int(torc['o'])}", font=("Arial", 8, "bold"), fill="#ff3333")

    # --- 5. ПРАВИЛЬНЫЕ СТРЕЛКИ НАПРАВЛЕНИЯ ОСЕЙ В УГЛУ ---
    # По вашему ТЗ: X идет вверх, Y идет вправо!
    axis_x0, axis_y0 = 40, w_height - 50
    canvas.create_line(axis_x0, axis_y0, axis_x0, axis_y0 - 45, fill=COLOR_AXIS, arrow=tk.LAST, width=2)
    canvas.create_text(axis_x0 - 12, axis_y0 - 40, text="X", font=("Arial", 10, "bold"), fill=COLOR_AXIS) 
    canvas.create_line(axis_x0, axis_y0, axis_x0 + 45, axis_y0, fill=COLOR_AXIS, arrow=tk.LAST, width=2)
    canvas.create_text(axis_x0 + 40, axis_y0 + 12, text="Y", font=("Arial", 10, "bold"), fill=COLOR_AXIS) 
    canvas.create_text(axis_x0 - 10, axis_y0 + 10, text="0", font=("Arial", 8, "bold"), fill=COLOR_AXIS)

# =========================================================================
# 🔲 РАЗДЕЛ 4: ОТРИСОВКА ВЫРАВНИВАНИЯ ПЛОСКОСТИ ЖЕРТВЕННИКА ИЛИ ЩИТОВ
# =========================================================================
def draw_plane_alignment_engine(canvas, entries, strategy_text):
    """Визуализирует зону выравнивания плоскости стола и траекторию змейки"""
    canvas.delete("all")
    w_width, w_height = get_safe_canvas_size(canvas)

    try:
        size_y = float(entries["size_y"].get()) if entries["size_y"].get() else 1000.0
        size_x = float(entries["size_x"].get()) if entries["size_x"].get() else 600.0
        tool_d = float(entries["tool_d"].get()) if entries["tool_d"].get() else 35.0
        overlap = float(entries["overlap"].get()) if entries["overlap"].get() else 40.0
    except ValueError:
        return

    # Задаем отступы вокруг зоны реза на экране
    total_y = size_y + 150.0
    total_x = size_x + 150.0

    scale_x = (w_width - 180) / total_y
    scale_y = (w_height - 180) / total_x
    scale = min(scale_x, scale_y)

    start_x = 90
    board_h = size_x * scale # Высота прямоугольника по оси X
    board_w_px = size_y * scale # Ширина прямоугольника по оси Y
    board_y = 80 + (w_height - 180 - board_h) / 2

    # 1. ЧЕРТИМ СЕРУЮ ЗОНУ СТОЛА (Жертвенник станка ЧПУ)
    canvas.create_rectangle(start_x, board_y, start_x + board_w_px, board_y + board_h, 
                            fill="#e1e1e1", outline="#888888", width=2)
    canvas.create_text(start_x + board_w_px/2, board_y + board_h/2, 
                       text="ЗОНА ВЫРАВНИВАНИЯ ПЛОСКОСТИ", font=("Arial", 10, "bold"), fill="#aaaaaa")

    # 2. РИСУЕМ ПОДПИСИ ТЕКУЩЕЙ СТРАТЕГИИ
    canvas.create_text(15, 10, text=f"Операция: ВЫРАВНИВАНИЕ СТОЛА", font=("Arial", 10, "bold"), fill="#444444", anchor=tk.NW)
    canvas.create_text(15, 26, text=f"Траектория фрезы: {strategy_text.upper()}", font=("Arial", 9, "italic"), fill="#1d4182", anchor=tk.NW)

    # 3. СИМУЛЯЦИЯ ТРАЕКТОРИИ ПРОХОДОВ ЗМЕЙКИ ЧПУ СВЕТЛЫМИ ТОНКИМИ ЛИНИЯМИ
    step_mm = tool_d * (1.0 - (overlap / 100.0))
    if step_mm <= 1.0: step_mm = 10.0
    
    step_px = step_mm * scale
    
    if strategy_text == "Зигзаг по Y":
        curr_x_px = 0.0
        idx = 0
        while curr_x_px <= board_h:
            # Чередуем проходы змейки вперед-назад вдоль оси Y по ТЗ
            if idx % 2 == 0:
                canvas.create_line(start_x + curr_x_px, board_y, start_x + curr_x_px, board_y + board_h, fill="#4a90e2", width=1, arrow=tk.LAST)
            else:
                canvas.create_line(start_x + curr_x_px, board_y + board_h, start_x + curr_x_px, board_y, fill="#4a90e2", width=1, arrow=tk.LAST)
            
            # Соединительный горизонтальный шаг фрезы
            if curr_x_px + step_px <= board_h:
                canvas.create_line(start_x + curr_x_px, board_y + (board_h if idx % 2 == 0 else 0), 
                                   start_x + curr_x_px + step_px, board_y + (board_h if idx % 2 == 0 else 0), fill="#4a90e2", width=1)
            curr_x_px += step_px
            idx += 1
    else:
        # Зигзаг по X (вертикальные проходы)
        curr_y_px = 0.0
        idx = 0
        while curr_y_px <= board_w_px:
            if idx % 2 == 0:
                canvas.create_line(start_x, board_y + curr_y_px, start_x + board_w_px, board_y + curr_y_px, fill="#4a90e2", width=1, arrow=tk.LAST)
            else:
                canvas.create_line(start_x + board_w_px, board_y + curr_y_px, start_x, board_y + curr_y_px, fill="#4a90e2", width=1, arrow=tk.LAST)
            
            if curr_y_px + step_px <= board_w_px:
                canvas.create_line(start_x + (board_w_px if idx % 2 == 0 else 0), board_y + curr_y_px, 
                                   start_x + (board_w_px if idx % 2 == 0 else 0), board_y + curr_y_px + step_px, fill="#4a90e2", width=1)
            curr_y_px += step_px
            idx += 1

    # 4. РАЗМЕРНЫЕ СТРЕЛКИ ВЫНОСОК СЕРЫМ ЦВЕТОМ БРЕНДА
    # Длина зоны Y (горизонтальная)
    canvas.create_line(start_x, board_y - 20, start_x + board_w_px, board_y - 20, fill=COLOR_DIM_LINE, arrow=tk.BOTH)
    canvas.create_text(start_x + board_w_px/2, board_y - 30, text=f"Y {int(size_y)}", font=FONT_DIM_BOLD, fill=COLOR_TEXT_MAIN)
    # Ширина зоны X (вертикальная)
    canvas.create_line(start_x - 20, board_y, start_x - 20, board_y + board_h, fill=COLOR_DIM_LINE, arrow=tk.BOTH)
    canvas.create_text(start_x - 45, board_y + board_h/2, text=f"X {int(size_x)}", font=FONT_DIM_BOLD, fill=COLOR_TEXT_MAIN)

    # Рисуем стрелочки ЧПУ осей в левом нижнем углу стола (X - вверх, Y - вправо)
    axis_x0, axis_y0 = 40, w_height - 50
    canvas.create_line(axis_x0, axis_y0, axis_x0, axis_y0 - 45, fill=COLOR_AXIS, arrow=tk.LAST, width=2)
    canvas.create_text(axis_x0 - 12, axis_y0 - 40, text="X", font=("Arial", 10, "bold"), fill=COLOR_AXIS) 
    canvas.create_line(axis_x0, axis_y0, axis_x0 + 45, axis_y0, fill=COLOR_AXIS, arrow=tk.LAST, width=2)
    canvas.create_text(axis_x0 + 40, axis_y0 + 12, text="Y", font=("Arial", 10, "bold"), fill=COLOR_AXIS) 
    canvas.create_text(axis_x0 - 10, axis_y0 + 10, text="0", font=("Arial", 8, "bold"), fill=COLOR_AXIS)

