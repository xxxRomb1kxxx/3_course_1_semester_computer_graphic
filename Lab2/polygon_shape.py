from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPainter, QTransform
from shape import Shape


class PolygonShape(Shape):
    """Класс для полигона"""
    def __init__(self, points):
        self.points = points  # Список QPointF

    def draw(self, painter: QPainter):
        painter.drawPolygon(*self.points)

    def transform(self, dx=0, dy=0, angle=0):
        if not self.points:
            return

        # Выбираем первую точку как центр вращения
        pivot = self.points[0]

        transform = QTransform()
        transform.translate(pivot.x(), pivot.y())
        transform.rotate(angle)
        transform.translate(-pivot.x(), -pivot.y())

        # Поворачиваем точки
        self.points = [transform.map(p) for p in self.points]

        # Сдвигаем полигоны
        self.points = [QPointF(p.x() + dx, p.y() + dy) for p in self.points]
