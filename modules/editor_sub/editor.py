import tkinter as tk
from modules.editor_sub import editor_engine
from modules.editor_sub import editor_toolbar
from modules.editor_sub import editor_joystick
from modules.editor_sub import editor_mouse


def load_editor_interface(params_frame, canvas, controller):
    """
    Главный диспетчер CAM-редактора ЧПУ.
    Освобождает пространство экрана и делегирует сборку специализированным модулям.
    """
    # 1. Динамически скрываем левую колонку станка и расширяем область
    if hasattr(controller.ui, 'left_column'):
        controller.ui.left_column.pack_forget()

    canvas.pack_forget()

    # 2. Очищаем холст от старых элементов изделий
    for widget in canvas.winfo_children(): 
        widget.destroy()
    canvas.delete("all")
    
    parent_frame = controller.ui.right_column
    if hasattr(parent_frame, 'toolbar_frame'):
        parent_frame.toolbar_frame.destroy()

    # 3. Создаем верхний Toolbar и возвращаем под него Canvas
    toolbar = tk.Frame(parent_frame, bg="#eaeaea", bd=1, relief=tk.GROOVE)
    toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(2, 2))
    parent_frame.toolbar_frame = toolbar 

    canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # 4. Считываем реальные размеры экрана
    canvas.update_idletasks()
    w_width = canvas.winfo_width() if canvas.winfo_width() > 100 else 1000
    w_height = canvas.winfo_height() if canvas.winfo_height() > 100 else 600

    import json # Добавляем системную библиотеку для работы с файлами проектов

    # Глобальное состояние отображения чертежа (добавили project_path)
    state = {
        "pan_x": 0,
        "pan_y": 0,
        "scale": 100.0,
        "active_tool": tk.StringVar(value="move_item"),
        "selected_id": None,
        "project_path": None  # Тот самый путь к текущему открытому файлу .cam
    }

    # 5. Отрисовываем стартовую сетку миллиметровки
    editor_engine.draw_editor_grid(canvas, w_width, w_height, 10, state["pan_x"], state["pan_y"])

    # 6. Подключаем изолированные модули интерфейса и логики мыши
    editor_toolbar.build_toolbar(toolbar, canvas, state)
    editor_joystick.build_joystick(canvas, state, w_width, w_height)
    editor_mouse.init_mouse_logic(canvas, state)
