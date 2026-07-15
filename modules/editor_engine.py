import tkinter as tk

# Глобальные списки для хранения геометрии нарисованных объектов (для истории назад/вперед)
DRAWN_ELEMENTS = []
HISTORY_REDO = []

def calculate_scale_dimensions(current_w, current_h, scale_pct=100.0, target_w=None, target_h=None):
    """Математика масштабирования элементов чертежа"""
    if target_w is not None and current_w > 0:
        ratio = target_w / current_w
        return ratio, target_w, current_h * ratio
    if target_h is not None and current_h > 0:
        ratio = target_h / current_h
        return ratio, current_w * ratio, target_h
    ratio = scale_pct / 100.0
    return ratio, current_w * ratio, current_h * ratio

def draw_editor_grid(canvas, w_width, w_height, grid_step=10, offset_x=0, offset_y=0):
    """Отрисовка точной координатной сетки ЧПУ стола с учетом смещения панорамы"""
    canvas.delete("grid_line")
    
    # Вертикальные линии
    start_x = int(offset_x % grid_step)
    for x in range(start_x, w_width, grid_step):
        real_x = x - offset_x
        line_color = "#e5e5e5" if real_x % 50 != 0 else "#cccccc"
        canvas.create_line(x, 0, x, w_height, fill=line_color, width=1, tags="grid_line")
        
    # Горизонтальные линии
    start_y = int(offset_y % grid_step)
    for y in range(start_y, w_height, grid_step):
        real_y = y - offset_y
        line_color = "#e5e5e5" if real_y % 50 != 0 else "#cccccc"
        canvas.create_line(0, y, w_width, y, fill=line_color, width=1, tags="grid_line")

def place_vector_text_on_table(canvas, text_string, start_x, start_y, font_name="Arial", size_mm=20):
    """Размещает текст на холсте редактора"""
    if not text_string: return
    font_size_px = int(size_mm)
    if font_size_px < 5: font_size_px = 5
    
    item_id = canvas.create_text(
        start_x, start_y, text=text_string, font=(font_name, font_size_px, "bold"),
        fill="#1d4182", anchor=tk.CENTER, tags="vector_text"
    )
    DRAWN_ELEMENTS.append(("text", item_id, text_string, start_x, start_y, font_name, size_mm))
    HISTORY_REDO.clear()

def import_dxf_file_engine(canvas, file_path, offset_x=0, offset_y=0):
    """
    Движок импорта DXF AutoCAD. 
    Имитирует загрузку векторов на стол для визуальной проверки структуры.
    """
    if not file_path: return
    # Для демонстрации рисуем условный сложный контур-декор из AutoCAD в центре стола
    cx, cy = 400 + offset_x, 200 + offset_y
    r = 80
    
    # Создаем тестовую группу векторов DXF
    i1 = canvas.create_rectangle(cx - r, cy - r, cx + r, cy + r, outline="#555555", width=1, tags="dxf_group")
    i2 = canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#1d4182", width=1, tags="dxf_group")
    i3 = canvas.create_line(cx - r, cy, cx + r, cy, fill="#999999", tags="dxf_group")
    i4 = canvas.create_line(cx, cy - r, cx, cy + r, fill="#999999", tags="dxf_group")
    
    DRAWN_ELEMENTS.append(("dxf", [i1, i2, i3, i4]))
    print(f"[DXF Движок] Загружен файл: {file_path}. Найдено векторов: 4 шт.")


def find_nearest_snap_point(canvas, current_x, current_y, snap_radius=15):
    """
    Сканирует все нарисованные линии и объекты на холсте.
    Если курсор мыши находится в радиусе snap_radius от конца любой линии,
    функция возвращает (True, snap_x, snap_y). Иначе возвращает (False, current_x, current_y).
    """
    # Сканируем только объекты с тегом "drawn_line" (наши нарисованные фигуры)
    all_lines = canvas.find_withtag("drawn_line")
    
    for item_id in all_lines:
        # Проверяем, является ли объект линией (у нее 4 координаты: x1, y1, x2, y2)
        if canvas.type(item_id) == "line":
            coords = canvas.coords(item_id)
            if len(coords) >= 4:
                x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
                
                # Проверяем расстояние до начальной точки линии (x1, y1)
                dist1 = ((current_x - x1)**2 + (current_y - y1)**2)**0.5
                if dist1 <= snap_radius:
                    return True, x1, y1
                    
                # Проверяем расстояние до конечной точки линии (x2, y2)
                dist2 = ((current_x - x2)**2 + (current_y - y2)**2)**0.5
                if dist2 <= snap_radius:
                    return True, x2, y2
                    
        # Проверяем углы прямоугольников (у прямоугольника 4 координаты: x1, y1, x2, y2)
        elif canvas.type(item_id) == "rectangle":
            coords = canvas.coords(item_id)
            if len(coords) == 4:
                x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
                # Углы: (x1,y1), (x2,y1), (x1,y2), (x2,y2)
                corners = [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]
                for cx, cy in corners:
                    dist = ((current_x - cx)**2 + (current_y - cy)**2)**0.5
                    if dist <= snap_radius:
                        return True, cx, cy
                        
    return False, current_x, current_y


# =========================================================================
# ⚙️ ТЕХНОЛОГИЧЕСКИЙ ПАСПОРТ СТАНКА (Параметры УП по умолчанию)
# =========================================================================
CNC_SETTINGS = {
    "z_safe": "20.0",     # Безопасная высота холостых ходов G0 (мм)
    "z_clear": "5.0",     # Плоскость отвода/подвода (мм)
    "feed_xy": "3000",    # Рабочая подача обхода контура F (мм/мин)
    "feed_z": "600",      # Скорость вертикального врезания фрезы (мм/мин)
    "spindle_s": "18000"  # Обороты шпинделя станка S (об/мин)
}

def update_cnc_settings(z_safe, z_clear, feed_xy, feed_z, spindle_s):
    """Обновляет глобальные параметры станка ЧПУ из интерфейса"""
    CNC_SETTINGS["z_safe"] = str(z_safe)
    CNC_SETTINGS["z_clear"] = str(z_clear)
    CNC_SETTINGS["feed_xy"] = str(feed_xy)
    CNC_SETTINGS["feed_z"] = str(feed_z)
    CNC_SETTINGS["spindle_s"] = str(spindle_s)
    print(f"[ЧПУ Конфиг] Обновлены глобальные параметры: {CNC_SETTINGS}")

def scale_all_drawn_elements_engine(canvas, scale_pct=100.0, target_w=None):
    """
    Вычисляет габаритный центр всех объектов на холсте и пропорционально
    масштабирует их координаты в процентах или под точный размер в мм.
    """
    # Собираем все пользовательские элементы (линии, текст, dxf)
    all_items = canvas.find_withtag("drawn_line") + canvas.find_withtag("vector_text") + canvas.find_withtag("dxf_group")
    if not all_items:
        return
        
    # 1. Находим текущие общие границы (Bounding Box) всех элементов на столе
    coords_list = []
    for item in all_items:
        bbox = canvas.bbox(item)
        if bbox:
            coords_list.extend([bbox[0], bbox[1], bbox[2], bbox[3]])
            
    if not coords_list:
        return
        
    x_min, y_min = min(coords_list[::2]), min(coords_list[1::2])
    x_max, y_max = max(coords_list[::2]), max(coords_list[1::2])
    
    current_w = x_max - x_min
    current_h = y_max - y_min
    
    # Находим геометрический центр группы объектов
    cx = x_min + (current_w / 2.0)
    cy = y_min + (current_h / 2.0)
    
    # 2. Вычисляем коэффициент масштабирования (ratio)
    if target_w is not None and target_w > 0 and current_w > 0:
        ratio = target_w / current_w
    else:
        ratio = scale_pct / 100.0
        
    if ratio <= 0.01:
        return
        
    # 3. Применяем коэффициент к каждому объекту
    for item in all_items:
        if canvas.type(item) == "text":
            # Для текста масштабируем его позицию и размер шрифта
            curr_coords = canvas.coords(item)
            if len(curr_coords) >= 2:
                new_x = cx + (curr_coords[0] - cx) * ratio
                new_y = cy + (curr_coords[1] - cy) * ratio
                canvas.coords(item, new_x, new_y)
                
                # Читаем старый шрифт и увеличиваем/уменьшаем его размер
                f_current = canvas.itemcget(item, "font")
                # Строка вида "{Arial} 30 bold"
                try:
                    parts = f_current.split()
                    f_name = parts[0].replace("{", "").replace("}", "")
                    f_size = int(parts[1])
                    new_size = max(5, int(f_size * ratio))
                    canvas.itemconfig(item, font=(f_name, new_size, "bold"))
                except Exception:
                    pass
        else:
            # Для линий и прямоугольников встроенная функция Tkinter делает всё сама идеально!
            canvas.scale(item, cx, cy, ratio, ratio)
            
    print(f"[ЧПУ Масштаб] Элементы пересчитаны с коэффициентом {ratio:.4f}")



