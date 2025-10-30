from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPainter, QPen, QColor, QAction, QBrush
from shapes import Shape


class PainterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Painter")
        self.setGeometry(100, 100, 800, 600)

        self.current_shape = None
        self.shapes = []

        self.create_menu()

    def create_menu(self):
        menubar = self.menuBar()
        shapes_menu = menubar.addMenu("Фигуры")

        square_action = QAction("Сруглённый квадрат", self)
        square_action.triggered.connect(lambda: self.select_shape("Сруглённый квадрат"))

        shapes_menu.addAction(square_action)

    def select_shape(self, shape_name):
        self.current_shape = shape_name
        print(f"Выбран инструмент: {self.current_shape}")

    def mousePressEvent(self, event):
        if self.current_shape:
            new_shape = Shape(self.current_shape, event.position())
            self.shapes.append(new_shape)
            self.update()  

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(0, 0, 0), 2)
        painter.setPen(pen)

        for shape in self.shapes:
            x = int(shape.position.x())
            y = int(shape.position.y())

            if shape.shape_type == "Сруглённый квадрат":
                width = 60
                height = 120
                radius = 15

                brush = QBrush(QColor(0, 191, 255))
                painter.setBrush(brush)

                painter.drawRoundedRect(x - width//2, y - height//2, width, height, radius, radius)