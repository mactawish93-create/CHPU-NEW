import tkinter as tk
from tkinter import messagebox

def load_disk_module(product_name, params_frame, canvas, controller):
    """Динамически перенаправляет загрузку UI в файл конкретного диска"""
    try:
        if product_name == "Круглый":
            from modules.disks import round_disk
            round_disk.load_interface(params_frame, canvas, controller)
        elif product_name == "Квадро":
            from modules.disks import quadro_disk
            quadro_disk.load_interface(params_frame, canvas, controller)
        elif product_name == "Бабочка":
            # 🆕 НАПРАВЛЯЕМ КЛИК В НОВЫЙ ФАЙЛ ДИСКА БАБОЧКИ
            from modules.disks import babochka_disk
            babochka_disk.load_interface(params_frame, canvas, controller)
        else:
            canvas.delete("all")
            canvas.create_text(400, 200, text=f"[ Модуль '{product_name} диск' в процессе разработки ]", 
                               font=("Arial", 12), fill="gray")
    except Exception as e:
        messagebox.showerror("Ошибка роутера", f"Не удалось загрузить модуль диска:\n{str(e)}")

def generate_disk_gcode(product_name, inputs):
    """Динамически вызывает математический расчет G-кода из файла конкретного диска"""
    if product_name == "Круглый":
        from modules.disks import round_disk
        return round_disk.generate_gcode(inputs)
    elif product_name == "Квадро":
        from modules.disks import quadro_disk
        return quadro_disk.generate_gcode(inputs)
    elif product_name == "Бабочка":
        # 🆕 НАПРАВЛЯЕМ КЛИК НА РАСЧЕТ ОРИГИНАЛЬНОГО G-КОДА БАБОЧКИ
        from modules.disks import babochka_disk
        return babochka_disk.generate_gcode(inputs)
    else:
        return ["G21 G90", f"( УП для {product_name} диска еще не готова )", "M30"]
