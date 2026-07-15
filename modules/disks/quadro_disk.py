import tkinter as tk
from tkinter import ttk

def load_interface(params_frame, canvas, controller):
    """Генерирует интерфейс для Квадро-диска (идентичен круглому)"""
    for widget in canvas.winfo_children():
        widget.destroy()
    for widget in params_frame.winfo_children():
        widget.destroy()

    type_var = tk.StringVar(value="Глухой")          
    size_var = tk.StringVar(value="2000")            
    door_offset_var = tk.StringVar(value="0 мм")      
    entries = {}

    # Кнопки выбора типа диска
    type_frame = ttk.Frame(params_frame, padding=2)
    type_frame.pack(anchor=tk.NW, fill=tk.X, padx=10, pady=5)
    
    btn_solid = tk.Button(type_frame, text="Глухой", font=("Arial", 9, "bold"), bg="#4a90e2", fg="white", bd=1, relief=tk.RAISED, width=12)
    btn_door = tk.Button(type_frame, text="С проемом", font=("Arial", 9), bg="#eaeaea", fg="black", bd=1, relief=tk.FLAT, width=12)
    
    btn_solid.pack(side=tk.LEFT, padx=2)
    btn_door.pack(side=tk.LEFT, padx=2)

    content_frame = ttk.Frame(params_frame)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def toggle_disk_type(selected_type):
        type_var.set(selected_type)
        for widget in content_frame.winfo_children():
            widget.destroy()
        entries.clear()

        if selected_type == "Глухой":
            btn_solid.config(bg="#4a90e2", fg="white", relief=tk.RAISED, font=("Arial", 9, "bold"))
            btn_door.config(bg="#eaeaea", fg="black", relief=tk.FLAT, font=("Arial", 9))
            
            geo_frame = ttk.LabelFrame(content_frame, text=" Параметры диска ", padding=10)
            geo_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(geo_frame, text="Размер диска:").grid(row=0, column=0, sticky=tk.W, pady=3)
            combo_size = ttk.Combobox(geo_frame, values=["2000", "2150", "2300"], textvariable=size_var, state="readonly", width=10)
            combo_size.grid(row=0, column=1, padx=5, pady=3, sticky=tk.W)
            combo_size.bind("<<ComboboxSelected>>", lambda e: draw_preview(canvas, size_var, type_var, door_offset_var))

            ttk.Label(geo_frame, text="Глубина реза Z (мм):").grid(row=1, column=0, sticky=tk.W, pady=3)
            entry_z = ttk.Entry(geo_frame, width=10)
            entry_z.insert(0, "-45.0") 
            entry_z.grid(row=1, column=1, padx=5, pady=3, sticky=tk.W)
            entries["z_deep"] = entry_z
            entry_z.bind("<KeyRelease>", lambda e: draw_preview(canvas, size_var, type_var, door_offset_var))

        else:
            btn_solid.config(bg="#eaeaea", fg="black", relief=tk.FLAT, font=("Arial", 9))
            btn_door.config(bg="#4a90e2", fg="white", relief=tk.RAISED, font=("Arial", 9, "bold"))
            
            geo_frame = ttk.LabelFrame(content_frame, text=" Параметры диска ", padding=10)
            geo_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(geo_frame, text="Размер диска:").grid(row=0, column=0, sticky=tk.W, pady=3)
            combo_size = ttk.Combobox(geo_frame, values=["2000", "2150", "2300"], textvariable=size_var, state="readonly", width=10)
            combo_size.grid(row=0, column=1, padx=5, pady=3, sticky=tk.W)
            combo_size.bind("<<ComboboxSelected>>", lambda e: draw_preview(canvas, size_var, type_var, door_offset_var))

            door_frame = ttk.LabelFrame(content_frame, text=" Дверной проем ", padding=10)
            door_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(door_frame, text="Смещение двери:").grid(row=0, column=0, sticky=tk.W, pady=3)
            combo_offset = ttk.Combobox(door_frame, values=["0 мм", "100 мм", "150 мм"], textvariable=door_offset_var, state="readonly", width=10)
            combo_offset.grid(row=0, column=1, padx=5, pady=3, sticky=tk.W)
            combo_offset.bind("<<ComboboxSelected>>", lambda e: draw_preview(canvas, size_var, type_var, door_offset_var))

            ttk.Label(door_frame, text="Глубина реза Z (мм):").grid(row=1, column=0, sticky=tk.W, pady=3)
            entry_z = ttk.Entry(door_frame, width=10)
            entry_z.insert(0, "-45.0")
            entry_z.grid(row=1, column=1, padx=5, pady=3, sticky=tk.W)
            entries["z_deep"] = entry_z
            entry_z.bind("<KeyRelease>", lambda e: draw_preview(canvas, size_var, type_var, door_offset_var))

        controller.active_inputs = entries
        controller.active_inputs["size_var"] = size_var
        controller.active_inputs["type_var"] = type_var
        controller.active_inputs["door_offset_var"] = door_offset_var
        
        draw_preview(canvas, size_var, type_var, door_offset_var)

    btn_solid.config(command=lambda: toggle_disk_type("Глухой"))
    btn_door.config(command=lambda: toggle_disk_type("С проемом"))
    toggle_disk_type("Глухой")



def draw_preview(canvas, size_var, type_var, door_offset_var):
    """Квадро диск: перенаправляет отрисовку в общий disks_drawer"""
    from modules import disks_drawer
    disks_drawer.draw_quadro_disk_preview(canvas, size_var, type_var, door_offset_var)




def generate_gcode(inputs):
    """Сюда переедет точный алгоритм обхода Квадро-диска, когда вы скинете G-код!"""
    gcode = ["G21 G49 G80 G90", "( --- РАСЧЕТ КВАДРО ДИСКА ЧПУ --- )", "M30"]
    return gcode
