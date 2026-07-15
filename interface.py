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
        
        # =========================================================================
        # ВШИТЫЙ ЛОГОТИП (Base64 строка из файла string_code.txt)
        # Если вы еще не сгенерировали строку, здесь временно побудет заглушка
        # =========================================================================
        self.LOGO_DATA = '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'
        
        try:
            self.img_data = base64.b64decode(self.LOGO_DATA)
            self.logo_img = tk.PhotoImage(data=self.img_data)
            # Если логотип при первом запуске будет слишком большим, раскомментируйте строку ниже (уменьшит в 3 раза)
            # self.logo_img = self.logo_img.subsample(3, 3)
            self.logo_label = tk.Label(header, image=self.logo_img, bg="#ffffff")
        except Exception:
            # Заглушка: аккуратный текстовый блок, если картинка еще не вшита в код
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
        
        # Создаем верхние кнопки (функция описана ниже)
        self.create_rubric_buttons(btn_container)
        
        # Правый информационный блок станка ЧПУ
        self.status_right = tk.Label(header, text="Станок: Готов", font=("Arial", 9, "bold"),
                                     fg="#555555", bg="#ffffff", bd=1, relief=tk.GROOVE, width=18, height=2)
        self.status_right.pack(side=tk.RIGHT, padx=15, pady=5)
        
        # --- 2. ОСНОВНАЯ РАБОЧАЯ ОБЛАСТЬ (НИЗ) ---
        main_area = tk.Frame(self.root, bg=self.COLOR_BG)
        main_area.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая колонка (Параметры текущей вкладки + Кнопка действия)
        left_column = tk.Frame(main_area, width=280, bg=self.COLOR_BG)
        left_column.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_column.pack_propagate(False) # Блокируем сжатие колонки
        
        # Динамическая рамка параметров
        self.params_frame = tk.LabelFrame(
            left_column, 
            text=" Параметры изделия ", 
            font=("Arial", 9, "bold"),
            fg=self.COLOR_DEEP_BLUE, 
            bg=self.COLOR_BG
        )
        self.params_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # ЖЕСТКО ЗАКРЕПЛЕННАЯ НИЖНЯЯ КНОПКА (Синяя, текст белый)
        self.gen_btn = tk.Button(
            left_column, 
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
        right_column = tk.LabelFrame(
            main_area, 
            text=" Визуализация выбранных параметров ", 
            font=("Arial", 9, "bold"),
            fg=self.COLOR_DEEP_BLUE, 
            bg=self.COLOR_BG
        )
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        
        # Наш основной холст для чертежей
        self.canvas = tk.Canvas(right_column, bg="#ffffff", bd=1, relief=tk.SUNKEN)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_rubric_buttons(self, container):
        """Создание кнопок верхнего меню с выпадающим списком Пазировки"""
        # --- 🆕 1. ВЫПАДАЮЩЕЕ МЕНЮ 'ПАЗИРОВКА' (Вместо Труб) ---
        self.menu_paz = tk.Menu(self.root, tearoff=0, font=("Arial", 10), bg="#ffffff", 
                                 fg=self.COLOR_DEEP_BLUE, activebackground=self.COLOR_LIGHT_BLUE)
        self.menu_paz.add_command(label="Пазировка Бани", command=lambda: self.controller.select_product("Пазировка", "Бани"))
        self.menu_paz.add_command(label="Произвольная пазировка", command=lambda: self.controller.select_product("Пазировка", "Произвольная"))
        self.menu_paz.add_command(label="Выравнивание плоскости", command=lambda: self.controller.select_product("Пазировка", "Выравнивание"))
        
        btn_paz = ttk.Button(container, text="Пазировка ▾", style='Header.TButton')
        btn_paz.pack(side=tk.LEFT, padx=3)
        btn_paz.bind("<Button-1>", lambda e: self.show_dropdown(e, self.menu_paz))
        
        # 2. Кнопка "Диски" с полным выпадающим подменю из 5 изделий
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

        
        # 3. Кнопка "Декор" с выпадающим подменю
        self.menu_decor = tk.Menu(self.root, tearoff=0, font=("Arial", 10), bg="#ffffff", 
                                  fg=self.COLOR_DEEP_BLUE, activebackground=self.COLOR_LIGHT_BLUE)
        self.menu_decor.add_command(label="Элемент Фасада", command=lambda: self.controller.select_product("Декор", "Фасад"))
        self.menu_decor.add_command(label="Розетка Геометрическая", command=lambda: self.controller.select_product("Декор", "Розетка"))
        
        btn_decor = ttk.Button(container, text="Декор ▾", style='Header.TButton')
        btn_decor.pack(side=tk.LEFT, padx=3)
        btn_decor.bind("<Button-1>", lambda e: self.show_dropdown(e, self.menu_decor))
        
        # 4. Кнопка "Надписи" с выпадающим подменю
        self.menu_text = tk.Menu(self.root, tearoff=0, font=("Arial", 10), bg="#ffffff", 
                                 fg=self.COLOR_DEEP_BLUE, activebackground=self.COLOR_LIGHT_BLUE)
        self.menu_text.add_command(label="Гравировка текста", command=lambda: self.controller.select_product("Надписи", "Гравировка"))
        
        btn_text = ttk.Button(container, text="Надписи ▾", style='Header.TButton')
        btn_text.pack(side=tk.LEFT, padx=3)
        btn_text.bind("<Button-1>", lambda e: self.show_dropdown(e, self.menu_text))
        
        # 5. Новая кнопка "Просмотр G-кода"
        btn_gcode_view = ttk.Button(container, text="Просмотр G-кода", style='Header.TButton', 
                                    command=lambda: self.controller.select_rubric("Просмотр G-кода"))
        btn_gcode_view.pack(side=tk.LEFT, padx=3)
        
        # 6. Кнопка "Графический редактор"
        btn_editor = ttk.Button(container, text="Графический редактор", style='Header.TButton', 
                                command=lambda: self.controller.select_rubric("Редактор"))
        btn_editor.pack(side=tk.LEFT, padx=3)

    def show_dropdown(self, event, menu):
        """Отображает всплывающее меню строго под нажатой кнопкой"""
        menu.post(event.widget.winfo_rootx(), event.widget.winfo_rooty() + event.widget.winfo_height())
