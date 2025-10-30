from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QAction, QPainter, QPen, QColor
from PyQt6.QtWidgets import QMainWindow, QInputDialog

from polygon_shape import PolygonShape


class PainterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Painter – Полигоны")
        self.setGeometry(100, 100, 800, 600)

        self.setStyleSheet("""
                    QMainWindow {
                        background-color: white;
                    }
                    QMenuBar {
                        background-color: #f0f0f0;
                        color: black;
                        border-bottom: 1px solid #cccccc;
                    }
                    QMenuBar::item {
                        padding: 5px 10px;
                        background: transparent;
                    }
                    QMenuBar::item:selected {
                        background-color: #d0d0d0;
                    }
                    QMenuBar::item:pressed {
                        background-color: #c0c0c0;
                    }
                    QMenu {
                        background-color: white;
                        color: black;
                        border: 1px solid #cccccc;
                    }
                    QMenu::item {
                        padding: 5px 20px;
                    }
                    QMenu::item:selected {
                        background-color: #e0e0e0;
                    }
                """)

        self.shapes = []
        self.current_shape_type = None
        self.selected_shape = None

        self.create_menu()

    def create_menu(self):
        menubar = self.menuBar()

        shapes_menu = menubar.addMenu("Фигуры")
        polygon_action = QAction("Полигон", self)
        polygon_action.triggered.connect(self.add_polygon)
        shapes_menu.addAction(polygon_action)

        transform_menu = menubar.addMenu("Трансформации")

        move_action = QAction("Перенести", self)
        move_action.triggered.connect(self.move_shape)
        transform_menu.addAction(move_action)

        rotate_action = QAction("Повернуть", self)
        rotate_action.triggered.connect(self.rotate_shape)
        transform_menu.addAction(rotate_action)

    def add_polygon(self):
        """Добавляем полигон в список фигур"""
        # Рисуем "песочные часы" из картинки
        size = 100
        x, y = 300, 200

        points = [
            QPointF(x, y),                # верхняя вершина
            QPointF(x + size, y),         # правая верхняя
            QPointF(x + size / 2, y + size / 2),  # центр
            QPointF(x + size, y + size),  # правая нижняя
            QPointF(x, y + size),         # нижняя левая
            QPointF(x + size / 2, y + size / 2)   # центр повторно
        ]

        polygon = PolygonShape(points)
        self.shapes.append(polygon)
        self.selected_shape = polygon
        self.update()

    def move_shape(self):
        """Перемещаем выбранный полигон"""
        if not self.selected_shape:
            return

        dx, ok1 = QInputDialog.getInt(self, "Сдвиг по X", "Введите смещение по X:", 0)
        if not ok1:
            return
        dy, ok2 = QInputDialog.getInt(self, "Сдвиг по Y", "Введите смещение по Y:", 0)
        if not ok2:
            return

        self.selected_shape.transform(dx=dx, dy=dy)
        self.update()

    def rotate_shape(self):
        """Поворачиваем выбранный полигон"""
        if not self.selected_shape:
            return

        angle, ok = QInputDialog.getDouble(self, "Поворот", "Введите угол поворота (градусы):", 0)
        if not ok:
            return

        self.selected_shape.transform(angle=angle)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(0, 0, 0), 2)
        painter.setPen(pen)

        for shape in self.shapes:
            shape.draw(painter)