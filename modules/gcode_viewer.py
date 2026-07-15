import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re

def load_viewer_interface(params_frame, canvas, controller):
    """Строит левую панель со списком строк G-кода и настраивает горячие клавиши"""
    # Очищаем холст и панель от старых элементов/кнопок
    for widget in canvas.winfo_children():
        widget.destroy()
    for widget in params_frame.winfo_children():
        widget.destroy()

    # Сбрасываем и принудительно задаем начальный зум для нового файла
    canvas.zoom_factor = 1.0

    # Перенастраиваем нижнюю левую кнопку приложения
    controller.ui.gen_btn.config(
        text="ВЫБРАТЬ ФАЙЛ G-КОДА", 
        bg="#26529c", 
        fg="white",
        command=lambda: open_gcode_file(params_frame, canvas, controller)
    )

    # Заголовок левой панели
    lbl_title = ttk.Label(params_frame, text="Содержимое УП:", font=("Arial", 10, "bold"))
    lbl_title.pack(anchor=tk.NW, padx=10, pady=(5, 2))

    # Контейнер для текстового списка со скроллбаром
    list_frame = ttk.Frame(params_frame)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
    code_listbox = tk.Listbox(
        list_frame, 
        font=("Courier New", 9), 
        selectbackground="#43b5e4", 
        selectforeground="white",
        yscrollcommand=scrollbar.set,
        highlightthickness=0,
        bd=1
    )
    scrollbar.config(command=code_listbox.yview)
    
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    code_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    params_frame.viewer_widgets = {
        "listbox": code_listbox
    }

    # Создаем блок управления зумом в правом верхнем углу холста
    zoom_frame = tk.Frame(canvas, bg="#eaeaea", bd=1, relief=tk.GROOVE)
    # Используем pack с привязкой к правому верхнему углу (NE) с аккуратными отступами
    zoom_frame.pack(side=tk.TOP, anchor=tk.NE, padx=15, pady=15)

    # Принудительно объявляем функции зума, которые вызовут внутренний метод перерисовки
    def zoom_in():
        canvas.zoom_factor *= 1.2
        if hasattr(canvas, "trigger_redraw"): canvas.trigger_redraw()

    def zoom_out():
        canvas.zoom_factor /= 1.2
        if hasattr(canvas, "trigger_redraw"): canvas.trigger_redraw()

    def zoom_reset():
        canvas.zoom_factor = 1.0
        if hasattr(canvas, "trigger_redraw"): canvas.trigger_redraw()

    # Три аккуратные кнопки стандартного серого стиля ЧПУ
    tk.Button(zoom_frame, text=" + ", font=("Arial", 10, "bold"), bg="#ffffff", bd=1, width=3, command=zoom_in).pack(side=tk.LEFT, padx=1, pady=1)
    tk.Button(zoom_frame, text=" 0 ", font=("Arial", 10, "bold"), bg="#ffffff", bd=1, width=3, command=zoom_reset).pack(side=tk.LEFT, padx=1, pady=1)
    tk.Button(zoom_frame, text=" - ", font=("Arial", 10, "bold"), bg="#ffffff", bd=1, width=3, command=zoom_out).pack(side=tk.LEFT, padx=1, pady=1)

    # Начальное состояние чертежа
    canvas.delete("all")
    canvas.create_text(400, 200, text="[ Нажмите кнопку 'ВЫБРАТЬ ФАЙЛ G-КОДА' слева внизу ]", font=("Arial", 12), fill="gray")


def open_gcode_file(params_frame, canvas, controller):
    """Открывает файл, заполняет список строк и активирует отслеживание клавиш"""
    file_path = filedialog.askopenfilename(
        title="Открыть управляющую программу ЧПУ",
        filetypes=[("Файлы ЧПУ (*.tap *.nc *.gcode *.txt)", "*.tap *.nc *.gcode *.txt"), ("Все файлы", "*.*")]
    )
    if not file_path:
        return

    import os
    file_name = os.path.basename(file_path)

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{str(e)}")
        return

    listbox = params_frame.viewer_widgets["listbox"]
    listbox.delete(0, tk.END)
    for line in lines:
        listbox.insert(tk.END, line.replace("\n", ""))

    listbox.select_set(0)
    listbox.focus_set()

    canvas.zoom_factor = 1.0 # Базовый зум при открытии нового изделия
    parse_and_draw_gcode(lines, canvas, params_frame, file_name, controller)
def parse_and_draw_gcode(lines, canvas, params_frame, file_name, controller):
    """
    Разбирает G-код на траектории, выводит статистику в самый низ 
    и настраивает интерактивный трекинг вектора с клавиатуры.
    """
    map_line_to_vector = {}
    curr_x, curr_y = 0.0, 0.0
    is_rapid = True

    x_pattern = re.compile(r'X([-+]?\d*\.\d+|\d+)')
    y_pattern = re.compile(r'Y([-+]?\d*\.\d+|\d+)')

    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')

    # Шаг 1: Сбор экстремумов габаритов
    for idx, line in enumerate(lines):
        line_clean = line.strip().upper()
        if not line_clean or line_clean.startswith('('):
            continue

        if 'G0' in line_clean: is_rapid = True
        elif 'G1' in line_clean or 'G2' in line_clean or 'G3' in line_clean: is_rapid = False

        match_x = x_pattern.search(line_clean)
        match_y = y_pattern.search(line_clean)

        if match_x or match_y:
            old_x, old_y = curr_x, curr_y
            if match_x: curr_x = float(match_x.group(1))
            if match_y: curr_y = float(match_y.group(1))

            min_x, max_x = min(min_x, curr_x), max(max_x, curr_x)
            min_y, max_y = min(min_y, curr_y), max(max_y, curr_y)

            map_line_to_vector[idx] = {
                "type": "rapid" if is_rapid else "feed",
                "coords": (old_x, old_y, curr_x, curr_y)
            }

    if min_x == float('inf'): min_x, max_x = 0.0, 100.0
    if min_y == float('inf'): min_y, max_y = 0.0, 100.0

    size_x = max_x - min_x
    size_y = max_y - min_y

    # Функция интерактивной перерисовки холста (поддерживает кнопки зума)
    def redraw_canvas(event=None):
        canvas.delete("all")
        
        # Динамически считываем текущую ширину и высоту окна визуализации ЧПУ
        # Это позволяет тексту всегда быть в самом низу, а чертежу занимать максимум места
        w_width = canvas.winfo_width()
        w_height = canvas.winfo_height()
        
        # Если окно еще не прогрузилось в памяти, берем базовые безопасные размеры окна
        if w_width < 100: w_width = 800
        if w_height < 100: w_height = 480

        # Вычисляем увеличенный масштаб (базовый масштаб умножается на zoom_factor кнопок)
        # Доступная ширина увеличена, чертеж теперь займет максимум свободного места
        scale_x = (w_width - 150) / max(size_x, 1.0)
        scale_y = (w_height - 150) / max(size_y, 1.0)
        scale = min(scale_x, scale_y) * 0.95 * canvas.zoom_factor

        # Центрирование увеличенной траектории на экране ЧПУ
        offset_x = 90 + (w_width - 120 - size_x * scale) / 2 - min_x * scale
        offset_y = 60 + (w_height - 140 - size_y * scale) / 2 - min_y * scale

        def to_screen(x, y):
            sx = offset_x + x * scale
            sy = (offset_y + size_y * scale) - (y - min_y) * scale
            return sx, sy

        listbox = params_frame.viewer_widgets["listbox"]
        try:
            curr_sel = listbox.curselection()
            selected_idx = curr_sel[0] if curr_sel else -1
        except IndexError:
            selected_idx = -1

        # 1. Рисуем стандартные траектории G-кода
        for idx, vec in map_line_to_vector.items():
            if idx == selected_idx:
                continue
                
            x1, y1, x2, y2 = vec["coords"]
            sx1, sy1 = to_screen(x1, y1)
            sx2, sy2 = to_screen(x2, y2)
            
            if vec["type"] == "rapid":
                canvas.create_line(sx1, sy1, sx2, sy2, fill="#bcbcbc", dash=(2, 2), width=1)
            else:
                canvas.create_line(sx1, sy1, sx2, sy2, fill="#1d4182", width=2)

        # 2. Отрисовка активного выбранного вектора (Жирный голубой цвет бабочки)
        if selected_idx in map_line_to_vector:
            active_vec = map_line_to_vector[selected_idx]
            x1, y1, x2, y2 = active_vec["coords"]
            sx1, sy1 = to_screen(x1, y1)
            sx2, sy2 = to_screen(x2, y2)
            
            canvas.create_line(sx1, sy1, sx2, sy2, fill="#43b5e4", width=4)
            canvas.create_oval(sx2-4, sy2-4, sx2+4, sy2+4, fill="#ff4444", outline="white")

        # --- 3. НАПРАВЛЕНИЕ ОСЕЙ X И Y СТРЕЛКАМИ (ПРИЖАТЫ К НИЖНЕМУ ЛЕВОМУ КРАЮ) ---
        axis_x0, axis_y0 = 40, w_height - 65
        canvas.create_line(axis_x0, axis_y0, axis_x0, axis_y0 - 45, fill="#444444", arrow=tk.LAST, width=2)
        canvas.create_text(axis_x0 - 12, axis_y0 - 40, text="X", font=("Arial", 10, "bold"), fill="#444444")
        canvas.create_line(axis_x0, axis_y0, axis_x0 + 45, axis_y0, fill="#444444", arrow=tk.LAST, width=2)
        canvas.create_text(axis_x0 + 40, axis_y0 + 12, text="Y", font=("Arial", 10, "bold"), fill="#444444")

        # --- 4. ТЕКСТ СТАТИСТИКИ (НАМЕРТВО СДВИГНУТ В САМЫЙ НИЗ ОКНА, НИЖЕ ОСЕЙ) ---
        info_y = w_height - 20 # Зафиксировали ровно в 20 пикселях от нижнего среза окна
        stats_text = (
            f"Файл: [{file_name.upper()}]  |  Строк: {len(lines)}  |  "
            f"Габариты реза X: {size_x:.1f} мм, Y: {size_y:.1f} мм  |  "
            f"Границы: X [{min_x:.1f} : {max_x:.1f}] Y [{min_y:.1f} : {max_y:.1f}]  |  Зум: {canvas.zoom_factor:.1f}x"
        )
        canvas.create_text(w_width / 2, info_y, text=stats_text, font=("Arial", 9, "bold"), fill="#333333")

    # Привязываем ссылку на функцию перерисовки к самому объекту холста для внешних кнопок зума
    canvas.trigger_redraw = redraw_canvas

    # Настраиваем события Listbox
    listbox = params_frame.viewer_widgets["listbox"]
    listbox.bind("<<ListboxSelect>>", redraw_canvas)
    
    # Привязываем автоматический пересчет чертежа, если оператор меняет размеры самого окна Windows
    canvas.bind("<Configure>", lambda e: redraw_canvas())
    
    # Первая штатная отрисовка геометрии
    redraw_canvas()
