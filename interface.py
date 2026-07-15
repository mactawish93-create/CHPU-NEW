import tkinter as tk
from tkinter import ttk
import base64

class CNCMainWindow:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller 
        
        self.root.title("ЧПУ CAM Система — Бани Бабочки")
        self.root.geometry("1200x750")
        
        # --- ФИРМЕННЫЕ ЦВЕТА ИЗ ЛОГОТИПА КОМПАНИИ ---
        self.COLOR_DEEP_BLUE = "#1d4182"  # Глубокий синий (буквы)
        self.COLOR_LIGHT_BLUE = "#43b5e4" # Голубой (крылья бабочки)
        self.COLOR_GOLD = "#dca442"       # Золотой (бочка)
        self.COLOR_BG = "#f5f6f8"         # Нейтральный фон приложения
        
        self.root.config(bg=self.COLOR_BG)
        
        # Настройка системных стилей компонентов TTK
        self.style = ttk.Style()
        self.style.theme_use('vista')
        self.style.configure('Header.TButton', font=('Arial', 10, 'bold'), padding=6, foreground=self.COLOR_DEEP_BLUE)

        # --- 1. ВЕРХНЯЯ ПАНЕЛЬ (ШАПКА БРЕНДА) ---
        header = tk.Frame(self.root, bg="#ffffff", bd=1, relief=tk.SOLID)
        header.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        self.LOGO_DATA = 'заглушка'
        
        try:
            self.img_data = base64.b64decode(self.LOGO_DATA)
            self.logo_img = tk.PhotoImage(data=self.img_data)
            self.logo_label = tk.Label(header, image=self.logo_img, bg="#ffffff")
        except Exception:
            self.logo_label = tk.Label(
                header, 
                text="🦋 БАНИ БАБОЧКИ\nПарить легко!", 
                font=("Arial", 11, "bold"), 
                fg=self.COLOR_DEEP_BLUE, 
                bg="#ffffff",
                justify=tk.LEFT
            )
            
        self.logo_label.pack(side=tk.LEFT, padx=15, pady=5)
        
        # Контейнер для кнопок рубрик в шапке
        btn_container = tk.Frame(header, bg="#ffffff")
        btn_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15)
        
        # Создаем верхние кнопки
        self.create_rubric_buttons(btn_container)
        
        # Правый информационный блок станка ЧПУ
        self.status_right = tk.Label(header, text="Станок: Готов", font=("Arial", 9, "bold"),
                                     fg="#555555", bg="#ffffff", bd=1, relief=tk.GROOVE, width=18, height=2)
        self.status_right.pack(side=tk.RIGHT, padx=15, pady=5)
        
        # --- 2. ОСНОВНАЯ РАБОЧАЯ ОБЛАСТЬ (НИЗ) ---
        main_area = tk.Frame(self.root, bg=self.COLOR_BG)
        main_area.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая колонка (Параметры текущей вкладки + Кнопка действия)
        self.left_column = tk.Frame(main_area, width=280, bg=self.COLOR_BG)
        self.left_column.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.left_column.pack_propagate(False) # Блокируем сжатие колонки
        
        # Динамическая рамка параметров
        self.params_frame = tk.LabelFrame(
            self.left_column, 
            text=" Параметры изделия ", 
            font=("Arial", 9, "bold"),
            fg=self.COLOR_DEEP_BLUE, 
            bg=self.COLOR_BG
        )
        self.params_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # ЖЕСТКО ЗАКРЕПЛЕННАЯ НИЖНЯЯ КНОПКА (Синяя, текст белый)
        self.gen_btn = tk.Button(
            self.left_column, 
            text="СГЕНЕРИРОВАТЬ G-КОД", 
            font=("Arial", 11, "bold"),
            bg=self.COLOR_DEEP_BLUE, 
            fg="white", 
            activebackground=self.COLOR_LIGHT_BLUE,
            activeforeground="white", 
            bd=0, 
            height=2, 
            cursor="hand2",
            command=self.controller.on_generate_click
        )
        self.gen_btn.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Правая колонка (Большое поле визуализации векторов)
        self.right_column = tk.LabelFrame(
            main_area, 
            text=" Визуализация выбранных параметров ", 
            font=("Arial", 9, "bold"),
            fg=self.COLOR_DEEP_BLUE, 
            bg=self.COLOR_BG
        )
        self.right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        
        # Наш основной холст для чертежей
        self.canvas = tk.Canvas(self.right_column, bg="#ffffff", bd=1, relief=tk.SUNKEN)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_rubric_buttons(self, container):
        """Создание кнопок верхнего меню с выпадающим списком Пазировки"""
        self.menu_paz = tk.Menu(self.root, tearoff=0, font=("Arial", 10), bg="#ffffff", 
                                 fg=self.COLOR_DEEP_BLUE, activebackground=self.COLOR_LIGHT_BLUE)
        self.menu_paz.add_command(label="Пазировка Бани", command=lambda: self.controller.select_product("Пазировка", "Бани"))
        self.menu_paz.add_command(label="Произвольная пазировка", command=lambda: self.controller.select_product("Пазировка", "Произвольная"))
        self.menu_paz.add_command(label="Выравнивание плоскости", command=lambda: self.controller.select_product("Пазировка", "Выравнивание"))
        
        btn_paz = ttk.Button(container, text="Пазировка ▾", style='Header.TButton')
        btn_paz.pack(side=tk.LEFT, padx=3)
        btn_paz.bind("<Button-1>", lambda e: self.show_dropdown(e, self.menu_paz))
        
        self.menu_disks = tk.Menu(self.root, tearoff=0, font=("Arial", 10), bg="#ffffff", 
                                  fg=self.COLOR_DEEP_BLUE, activebackground=self.COLOR_LIGHT_BLUE)
        
        self.menu_disks.add_command(label="1. Круглый диск", command=lambda: self.controller.select_product("Диски", "Круглый"))
        self.menu_disks.add_command(label="2. Квадро диск", command=lambda: self.controller.select_product("Диски", "Квадро"))
        self.menu_disks.add_command(label="3. БаБочка диск", command=lambda: self.controller.select_product("Диски", "Бабочка"))
        self.menu_disks.add_command(label="4. Викинг диск", command=lambda: self.controller.select_product("Диски", "Викинг"))
        self.menu_disks.add_command(label="5. КвадроХаус диск", command=lambda: self.controller.select_product("Диски", "КвадроХаус"))
        
        btn_disks = ttk.Button(container, text="Диски ▾", style='Header.TButton')
        btn_disks.pack(side=tk.LEFT, padx=3)
        btn_disks.bind("<Button-1>", lambda e: self.show_dropdown(e, self.menu_disks))

        self.menu_decor = tk.Menu(self.root, tearoff=0, font=("Arial", 10), bg="#ffffff", 
                                  fg=self.COLOR_DEEP_BLUE, activebackground=self.COLOR_LIGHT_BLUE)
        self.menu_decor.add_command(label="Элемент Фасада", command=lambda: self.controller.select_product("Декор", "Фасад"))
        self.menu_decor.add_command(label="Розетка Геометрическая", command=lambda: self.controller.select_product("Декор", "Розетка"))
        
        btn_decor = ttk.Button(container, text="Декор ▾", style='Header.TButton')
        btn_decor.pack(side=tk.LEFT, padx=3)
        btn_decor.bind("<Button-1>", lambda e: self.show_dropdown(e, self.menu_decor))
        
        self.menu_text = tk.Menu(self.root, tearoff=0, font=("Arial", 10), bg="#ffffff", 
                                 fg=self.COLOR_DEEP_BLUE, activebackground=self.COLOR_LIGHT_BLUE)
        self.menu_text.add_command(label="Гравировка текста", command=lambda: self.controller.select_product("Надписи", "Гравировка"))
        
        btn_text = ttk.Button(container, text="Надписи ▾", style='Header.TButton')
        btn_text.pack(side=tk.LEFT, padx=3)
        btn_text.bind("<Button-1>", lambda e: self.show_dropdown(e, self.menu_text))
        
        btn_gcode_view = ttk.Button(container, text="Просмотр G-кода", style='Header.TButton', 
                                    command=lambda: self.controller.select_rubric("Просмотр G-кода"))
        btn_gcode_view.pack(side=tk.LEFT, padx=3)
        
        btn_editor = ttk.Button(container, text="Графический редактор", style='Header.TButton', 
                                command=lambda: self.controller.select_rubric("Редактор"))
        btn_editor.pack(side=tk.LEFT, padx=3)

    def show_dropdown(self, event, menu):
        """Отображает всплывающее меню строго под нажатой кнопкой"""
        menu.post(event.widget.winfo_rootx(), event.widget.winfo_rooty() + event.widget.winfo_height())
