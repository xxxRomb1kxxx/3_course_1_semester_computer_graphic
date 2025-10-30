from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QLabel, QCheckBox)
from PyQt5.QtGui import QPainter, QPen, QColor, QPainterPath
from PyQt5.QtCore import Qt, QPointF
import sys


class SplinePainter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Painter - Составной сплайн Безье (C1)')
        self.setMinimumSize(800, 600)

        self.points = [] 
        self.drag_index = -1
        self.show_control = True

        btn_clear = QPushButton('Очистить')
        btn_clear.clicked.connect(self.clear_points)
        btn_build = QPushButton('Построить сплайн')
        btn_build.clicked.connect(self.rebuild_and_update)
        self.chk_control = QCheckBox('Показать вспомогательные точки')
        self.chk_control.setChecked(True)
        self.chk_control.stateChanged.connect(self.toggle_control)
        instr = QLabel('Левый клик: добавить | Перетащить: переместить | Правый клик по точке: удалить')

        hbox = QHBoxLayout()
        hbox.addWidget(btn_clear)
        hbox.addWidget(btn_build)
        hbox.addWidget(self.chk_control)
        hbox.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(hbox)
        layout.addWidget(instr)

        self.path = None 

    def toggle_control(self, state):
        self.show_control = state == Qt.Checked
        self.update()

    def clear_points(self):
        self.points = []
        self.path = None
        self.update()

    def rebuild_and_update(self):
        self.path = self.build_composite_bezier(self.points)
        self.update()

    def mousePressEvent(self, event):
        p = event.pos()
        if event.button() == Qt.LeftButton:
            idx = self.find_nearest_point_index(p)
            if idx is not None and (self.points[idx] - p).manhattanLength() < 12:
                self.drag_index = idx
            else:
                self.points.append(QPointF(p))
                self.rebuild_and_update()
        elif event.button() == Qt.RightButton:
            idx = self.find_nearest_point_index(p)
            if idx is not None and (self.points[idx] - p).manhattanLength() < 12:
                del self.points[idx]
                self.rebuild_and_update()

    def mouseMoveEvent(self, event):
        if self.drag_index != -1:
            self.points[self.drag_index] = QPointF(event.pos())
            self.rebuild_and_update()

    def mouseReleaseEvent(self, event):
        self.drag_index = -1

    def find_nearest_point_index(self, pos):
        best_i = None
        best_d = None
        for i, pt in enumerate(self.points):
            d = (pt - pos).manhattanLength()
            if best_d is None or d < best_d:
                best_d = d
                best_i = i
        return best_i

    def build_composite_bezier(self, base_points):
        n = len(base_points)
        if n < 2:
            return None
        P = base_points

        T = [QPointF(0, 0) for _ in range(n)]
        if n == 2:
            T[0] = P[1] - P[0]
            T[1] = P[1] - P[0]
        else:
            for i in range(1, n-1):
                T[i] = (P[i+1] - P[i-1]) * 0.5
            T[0] = P[1] - P[0]
            T[n-1] = P[n-1] - P[n-2]

        control_pairs = [] 
        for i in range(n-1):
            C1 = P[i] + T[i] * (1.0/3.0)
            C2 = P[i+1] - T[i+1] * (1.0/3.0)
            control_pairs.append((C1, C2))

        path = QPainterPath(P[0])
        for i in range(n-1):
            C1, C2 = control_pairs[i]
            path.cubicTo(C1, C2, P[i+1])
        self._last_control_pairs = control_pairs
        return path

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), QColor(255, 255, 255))

        pen = QPen(Qt.black, 1)
        painter.setPen(pen)
        for pt in self.points:
            painter.drawEllipse(pt, 4, 4)

        if len(self.points) >= 2:
            pen = QPen(QColor(200, 200, 200), 1, Qt.DashLine)
            painter.setPen(pen)
            for i in range(len(self.points)-1):
                painter.drawLine(self.points[i], self.points[i+1])

        if self.path is not None:
            pen = QPen(QColor(10, 100, 200), 2)
            painter.setPen(pen)
            painter.drawPath(self.path)

        if getattr(self, '_last_control_pairs', None) and self.show_control:
            pen = QPen(QColor(180, 50, 50), 1, Qt.DashLine)
            painter.setPen(pen)
            for i, (C1, C2) in enumerate(self._last_control_pairs):
                painter.drawLine(self.points[i], C1)
                painter.drawLine(self.points[i+1], C2)

            pen = QPen(QColor(220, 120, 120), 1)
            painter.setPen(pen)
            for (C1, C2) in self._last_control_pairs:
                painter.drawEllipse(C1, 3, 3)
                painter.drawEllipse(C2, 3, 3)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = SplinePainter()

    def load_star():
        w.points = [QPointF(x, y) for x, y in [(200,150),(250,220),(320,240),(260,290),(280,360),(200,320),(120,360),(140,290),(80,240),(150,220),(200,150)]]
        w.rebuild_and_update()
    def load_triangle():
        w.points = [QPointF(x,y) for x,y in [(150,400),(400,400),(275,150),(150,400)]]
        w.rebuild_and_update()
    def load_house():
        w.points = [QPointF(x,y) for x,y in [(120,400),(360,400),(360,260),(240,160),(120,260),(120,400)]]
        w.rebuild_and_update()

    btns_layout = QHBoxLayout()
    btn_star = QPushButton('Загрузить: звезда')
    btn_star.clicked.connect(load_star)
    btn_tri = QPushButton('Загрузить: треугольник')
    btn_tri.clicked.connect(load_triangle)
    btn_house = QPushButton('Загрузить: дом')
    btn_house.clicked.connect(load_house)
    btns_layout.addWidget(btn_star)
    btns_layout.addWidget(btn_tri)
    btns_layout.addWidget(btn_house)
    w.layout().addLayout(btns_layout)

    w.show()
    sys.exit(app.exec_())
