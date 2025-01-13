import tkinter as tk
from tkinter import colorchooser
from abc import ABC, abstractmethod

# Базовый класс для фигуры
class Shape(ABC):
    def __init__(self, canvas, x1, y1, x2, y2, **kwargs):
        self.canvas = canvas
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.options = kwargs
        self.id = None  # Идентификатор объекта на холсте

    @abstractmethod
    def draw(self):
        pass

    def remove(self):
        """Удаляет фигуру с холста."""
        if self.id:
            self.canvas.delete(self.id)

# Класс для прямоугольника
class Rectangle(Shape):
    def draw(self):
        self.id = self.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, **self.options)

# Класс для овала
class Oval(Shape):
    def draw(self):
        self.id = self.canvas.create_oval(self.x1, self.y1, self.x2, self.y2, **self.options)

# Класс для линии
class Line(Shape):
    def draw(self):
        self.id = self.canvas.create_line(self.x1, self.y1, self.x2, self.y2, **self.options)

# Класс для рисования карандашом
class Pencil:
    def __init__(self, canvas, color):
        self.canvas = canvas
        self.color = color
        self.previous_x = None
        self.previous_y = None
        self.lines = []  # Список всех линий, нарисованных карандашом

    def draw(self, x, y):
        if self.previous_x and self.previous_y:
            line_id = self.canvas.create_line(self.previous_x, self.previous_y, x, y, fill=self.color)
            self.lines.append(line_id)  # Сохраняем идентификатор линии
        self.previous_x = x
        self.previous_y = y

    def reset(self):
        self.previous_x = None
        self.previous_y = None

    def remove(self):
        """Удаляет все линии, нарисованные карандашом."""
        for line in self.lines:
            self.canvas.delete(line)
        self.lines.clear()

# Класс для главного приложения
class GraphicEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Graphic Editor")

        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()

        self.shape = tk.StringVar(value="Rectangle")
        self.color = "blue"
        self.bg_color = "white"
        self.start_x = self.start_y = None
        self.pencil = None  # Инициализируем карандаш
        self.drawing_mode = "Shape"  # Режим рисования: по умолчанию "Shape"
        self.objects = []  # Список всех нарисованных объектов для undo

        self.create_toolbox()
        self.bind_events()

    def create_toolbox(self):
        toolbox = tk.Frame(self.root)
        toolbox.pack(side=tk.TOP, fill=tk.X)

        # Переключатель между режимами
        mode_label = tk.Label(toolbox, text="Mode:")
        mode_label.pack(side=tk.LEFT)

        mode_menu = tk.OptionMenu(toolbox, self.shape, "Rectangle", "Oval", "Line", "Pencil", command=self.switch_mode)
        mode_menu.pack(side=tk.LEFT)

        tk.Label(toolbox, text="Color:").pack(side=tk.LEFT)
        color_button = tk.Button(toolbox, text="Choose Color", command=self.choose_color)
        color_button.pack(side=tk.LEFT)

        # Добавляем кнопку для изменения цвета фона
        tk.Label(toolbox, text="Background Color:").pack(side=tk.LEFT)
        bg_color_button = tk.Button(toolbox, text="Choose Background Color", command=self.choose_bg_color)
        bg_color_button.pack(side=tk.LEFT)

        # Добавляем кнопку для отмены последнего действия
        undo_button = tk.Button(toolbox, text="Undo", command=self.undo)
        undo_button.pack(side=tk.LEFT)

    def switch_mode(self, selected_mode):
        """Переключает режим рисования (фигуры или карандаш)."""
        if selected_mode == "Pencil":
            self.drawing_mode = "Pencil"
        else:
            self.drawing_mode = "Shape"

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose Color")[1]
        if color_code:
            self.color = color_code

    def choose_bg_color(self):
        color_code = colorchooser.askcolor(title="Choose Background Color")[1]
        if color_code:
            self.bg_color = color_code
            self.canvas.config(bg=self.bg_color)

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<B1-Motion>", self.on_mouse_motion)

    def on_mouse_down(self, event):
        self.start_x, self.start_y = event.x, event.y

        # Если выбран режим карандаша, создаем объект карандаша
        if self.drawing_mode == "Pencil":
            self.pencil = Pencil(self.canvas, self.color)

    def on_mouse_up(self, event):
        if self.drawing_mode == "Shape":
            end_x, end_y = event.x, event.y
            shape_class = {
                "Rectangle": Rectangle,
                "Oval": Oval,
                "Line": Line,
            }[self.shape.get()]

            shape = shape_class(self.canvas, self.start_x, self.start_y, end_x, end_y, fill=self.color)
            shape.draw()
            self.objects.append(shape)  # Добавляем объект в список для отмены

        # Если это был режим карандаша, сбрасываем карандаш
        if self.pencil:
            self.pencil.reset()

    def on_mouse_motion(self, event):
        if self.drawing_mode == "Pencil" and self.pencil:
            self.pencil.draw(event.x, event.y)

    def undo(self):
        """Отменяет последнее действие."""
        if self.objects:
            last_object = self.objects.pop()  # Извлекаем последний объект из списка
            last_object.remove()  # Удаляем его с холста

        # Если карандаш рисовал линии, удаляем их
        if self.pencil:
            self.pencil.remove()
            self.pencil = None

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphicEditor(root)
    root.mainloop()