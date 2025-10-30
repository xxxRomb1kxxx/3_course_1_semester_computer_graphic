import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPixmap, QMouseEvent
from PyQt6.QtCore import Qt, QTimer, QPoint

# Константы
WINDOW_TITLE = "Hourglass spline (drag red points)"
IMG_SIZE = 600

# Фиксированные углы (чёрные точки)
TL = np.array([100, 100], dtype=float)   # верхний левый
TR = np.array([300, 100], dtype=float)   # верхний правый
BR = np.array([300, 300], dtype=float)   # нижний правый
BL = np.array([100, 300], dtype=float)   # нижний левый

# Красные контрольные точки (доступны для перетаскивания)
ctrl_pts = [
    np.array([160.0, 100.0]),  # верхняя левая контрол-пт (на уровне TL)
    np.array([240.0, 100.0]),  # верхняя правая контрол-пт (на уровне TR)
    np.array([240.0, 300.0]),  # нижняя правая контрол-пт (на уровне BR)
    np.array([160.0, 300.0]),  # нижняя левая контрол-пт (на уровне BL)
]

POINT_RADIUS = 8
drag_idx = None
TANGENT_SCALE = 0.3  # масштаб касательного вектора


def bezier_curve(p0, p1, p2, p3, n_points=60):
    """
    Кубическая Bézier-кривая между p0 и p3, с контрольными точками p1 и p2.
    Возвращает массив (N,2) целых координат.
    """
    t = np.linspace(0, 1, n_points)
    t2 = t * t
    t3 = t2 * t
    one_minus_t = 1 - t
    one_minus_t2 = one_minus_t * one_minus_t
    one_minus_t3 = one_minus_t2 * one_minus_t

    x = one_minus_t3 * p0[0] + 3 * one_minus_t2 * t * p1[0] + 3 * one_minus_t * t2 * p2[0] + t3 * p3[0]
    y = one_minus_t3 * p0[1] + 3 * one_minus_t2 * t * p1[1] + 3 * one_minus_t * t2 * p2[1] + t3 * p3[1]

    return np.array([x, y]).T.astype(int)


class HourglassWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(IMG_SIZE, IMG_SIZE)
        self.pixmap = QPixmap(self.size())
        self.update_pixmap()
        self.dragging = False
        self.drag_idx = None

    def update_pixmap(self):
        painter = QPainter(self.pixmap)
        painter.fillRect(0, 0, IMG_SIZE, IMG_SIZE, QColor(255, 255, 255))

        # Рисуем диагонали (синие толстые линии)
        pen = QPen(QColor(0, 0, 255), 3, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawLine(int(TL[0]), int(TL[1]), int(BR[0]), int(BR[1]))
        painter.drawLine(int(TR[0]), int(TR[1]), int(BL[0]), int(BL[1]))

        # --- Верхняя кривая: TL -> TR ---
        tangent_TL = ctrl_pts[0] - TL
        tangent_TR = ctrl_pts[1] - TR
        p1_top = TL + TANGENT_SCALE * tangent_TL
        p2_top = TR - TANGENT_SCALE * tangent_TR
        top_curve = bezier_curve(TL, p1_top, p2_top, TR, 60)
        self.draw_curve(painter, top_curve)

        # --- Нижняя кривая: BL -> BR ---
        tangent_BL = ctrl_pts[3] - BL
        tangent_BR = ctrl_pts[2] - BR
        p1_bottom = BL + TANGENT_SCALE * tangent_BL
        p2_bottom = BR - TANGENT_SCALE * tangent_BR
        bottom_curve = bezier_curve(BL, p1_bottom, p2_bottom, BR, 60)
        self.draw_curve(painter, bottom_curve)

        # Пунктирные линии от углов к контрольным точкам
        pen = QPen(QColor(200, 200, 200), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        self.draw_dashed_line(painter, TL, ctrl_pts[0])
        self.draw_dashed_line(painter, TR, ctrl_pts[1])
        self.draw_dashed_line(painter, BR, ctrl_pts[2])
        self.draw_dashed_line(painter, BL, ctrl_pts[3])

        # Чёрные углы
        pen = QPen(QColor(0, 0, 0), 1)
        brush = QBrush(QColor(0, 0, 0))
        painter.setPen(pen)
        painter.setBrush(brush)
        for p in (TL, TR, BR, BL):
            painter.drawEllipse(int(p[0]) - 5, int(p[1]) - 5, 10, 10)

        # Красные контрольные точки
        pen = QPen(QColor(0, 0, 0), 1)
        brush = QBrush(QColor(255, 0, 0))
        painter.setPen(pen)
        painter.setBrush(brush)
        for p in ctrl_pts:
            painter.drawEllipse(int(p[0]) - POINT_RADIUS, int(p[1]) - POINT_RADIUS, 2 * POINT_RADIUS, 2 * POINT_RADIUS)

        painter.end()

    def draw_curve(self, painter, curve):
        if len(curve) < 2:
            return
        pen = QPen(QColor(0, 0, 255), 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        for i in range(1, len(curve)):
            x1, y1 = curve[i-1]
            x2, y2 = curve[i]
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def draw_dashed_line(self, painter, a, b):
        ax, ay = int(a[0]), int(a[1])
        bx, by = int(b[0]), int(b[1])
        pen = QPen(QColor(200, 200, 200), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(ax, ay, bx, by)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)

    def mousePressEvent(self, event: QMouseEvent):
        global drag_idx
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            x, y = pos.x(), pos.y()
            for i, p in enumerate(ctrl_pts):
                dx = x - p[0]
                dy = y - p[1]
                if dx*dx + dy*dy <= (POINT_RADIUS + 4)**2:
                    drag_idx = i
                    break

    def mouseMoveEvent(self, event: QMouseEvent):
        global drag_idx
        if drag_idx is not None:
            pos = event.position().toPoint()
            x = float(pos.x())

            # Фиксируем Y-координату в зависимости от индекса
            if drag_idx == 0 or drag_idx == 1:  # верхние точки
                y = 100.0
            else:  # нижние точки
                y = 300.0

            ctrl_pts[drag_idx][0] = x
            ctrl_pts[drag_idx][1] = y

            self.update_pixmap()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        global drag_idx
        if event.button() == Qt.MouseButton.LeftButton:
            drag_idx = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(700, 700)
        self.central_widget = HourglassWidget()
        self.setCentralWidget(self.central_widget)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())