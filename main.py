import os
import tkinter as tk
from tkinter import messagebox

# Импортируем графическую оболочку
from interface import CNCMainWindow

# Импортируем независимые модули обработки изделий и CAM-инструментов
from modules import pipes 
from modules import gcode_viewer
from modules import editor
from modules import disks_router

class MainController:
    def __init__(self):
        self.root = tk.Tk()
        
        self.active_rubric = None
        self.active_product = None
        self.active_inputs = {} # Словарь для хранения ссылок на Entry
        
        # Инициализируем графический интерфейс приложения
        self.ui = CNCMainWindow(self.root, self)
        
        # При старте программы по умолчанию открываем пазировку бани
        self.select_product("Пазировка", "Бани")

        self.root.mainloop()

    def select_rubric(self, rubric_name):
        """Вызывается графической оболочкой при клике на верхние обычные кнопки"""
        self.active_rubric = rubric_name
        self.active_product = None
        
        # Возвращаем нижнюю левую кнопку к стандартному синему состоянию
        self.ui.gen_btn.config(
            text="СГЕНЕРИРОВАТЬ G-КОД", 
            bg=self.ui.COLOR_DEEP_BLUE, 
            fg="white",
            command=self.on_generate_click
        )
        
        self.clear_params_and_canvas()
        self.ui.params_frame.config(text=f" Параметры: {rubric_name} ")
        
        # Обновление геометрии окон Windows
        self.root.update_idletasks()
        
        if rubric_name == "Редактор":
            editor.load_editor_interface(self.ui.params_frame, self.ui.canvas, self)
        elif rubric_name == "Просмотр G-кода":
            gcode_viewer.load_viewer_interface(self.ui.params_frame, self.ui.canvas, self)

    def select_product(self, rubric_name, product_name):
        """Вызывается графической оболочкой при выборе конкретного подпункта"""
        self.active_rubric = rubric_name
        self.active_product = product_name
        
        self.ui.gen_btn.config(
            text="СГЕНЕРИРОВАТЬ G-КОД", 
            bg=self.ui.COLOR_DEEP_BLUE, 
            fg="white",
            command=self.on_generate_click
        )
        
        self.clear_params_and_canvas()
        self.ui.params_frame.config(text=f" {rubric_name} > {product_name} ")
        self.root.update_idletasks()
        
        # МАРШРУТИЗАТОР ДЛЯ ПАЗИРОВКИ
        if rubric_name == "Пазировка":
            if product_name == "Бани":
                pipes.load_pipe_interface(self.ui.params_frame, self.ui.canvas, self)
            elif product_name == "Произвольная":
                pipes.load_custom_paz_interface(self.ui.params_frame, self.ui.canvas, self)
            elif product_name == "Выравнивание":
                pipes.load_plane_interface(self.ui.params_frame, self.ui.canvas, self)
            else:
                self.ui.canvas.create_text(400, 250, text=f"Модуль {product_name} в разработке", font=("Arial", 12), fill="gray")
        
        # МАРШРУТИЗАТОР ДЛЯ ДИСКОВ
        elif rubric_name == "Диски":
            disks_router.load_disk_module(product_name, self.ui.params_frame, self.ui.canvas, self)

    def clear_params_and_canvas(self):
        """Очистка рабочих зон перед сменой рубрики"""
        for widget in self.ui.params_frame.winfo_children():
            widget.destroy()
        self.ui.canvas.delete("all")
        self.active_inputs.clear()
        
        # Отвязываем события мыши принудительно для защиты от багов
        self.ui.canvas.unbind("<Button-1>")
        self.ui.canvas.unbind("<B1-Motion>")
        self.ui.canvas.unbind("<ButtonRelease-1>")
        self.ui.canvas.unbind("<Button-3>")
        self.ui.canvas.unbind("<MouseWheel>")

    def on_generate_click(self):
        """Клик по нижней левой кнопке генерации кода"""
        if not self.active_rubric:
            messagebox.showwarning("Внимание", "Сначала выберите изделие или рубрику!")
            return
        
        try:
            # --- 1. МАРШРУТИЗАЦИЯ ДЛЯ РАЗДЕЛА ПАЗИРОВКИ ---
            if self.active_rubric == "Пазировка":
                if self.active_product == "Бани":
                    generated_code = pipes.generate_pipe_gcode(self.active_inputs)
                    filename = "board_output.tap"
                elif self.active_product == "Выравнивание":
                    generated_code = pipes.generate_plane_gcode(self.active_inputs)
                    filename = "plane_alignment.tap"
                else:
                    return

            # --- 2. МАРШРУТИЗАЦИЯ ДЛЯ РАЗДЕЛА ДИСКОВ ---
            elif self.active_rubric == "Диски":
                generated_code = disks_router.generate_disk_gcode(self.active_product, self.active_inputs)
                filename = f"{self.active_product.lower()}_disk_output.tap"
            else:
                return
                
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            file_path = os.path.join(desktop, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(generated_code))
                
            messagebox.showinfo("Успех", f"УП '{filename}' успешно сохранена на Рабочий стол!")
            
        except Exception as e:
            messagebox.showerror("Ошибка расчета", f"Не удалось сгенерировать код.\nОшибка: {str(e)}")


if __name__ == "__main__":
    app = MainController()
