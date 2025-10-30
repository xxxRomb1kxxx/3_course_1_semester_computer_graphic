from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QLabel, QCheckBox, QFileDialog, QSlider, QMessageBox)
from PyQt5.QtGui import (QPainter, QPen, QColor, QPainterPath, QPixmap, QImage,
                         QBrush, QPolygonF)
from PyQt5.QtCore import Qt, QPointF, QRectF
import sys


class RasterResource:
    """Класс для работы с растровыми ресурсами.

    Поддерживаемые операции:
    - загрузка из файла (QImage / QPixmap)
    - масштабирование с сохранением оригинала
    - получение QBrush на основе шаблона
    """
    def __init__(self, image=None):
        self.original = None
        self.pixmap = None
        if image is not None:
            self.set_image(image)

    def set_image(self, image):
        """Принимает QImage или QPixmap"""
        if isinstance(image, QPixmap):
            self.original = image.toImage()
        elif isinstance(image, QImage):
            self.original = image
        else:
            raise TypeError('image must be QImage or QPixmap')
        self.pixmap = QPixmap.fromImage(self.original)

    def load_from_file(self, filename):
        img = QImage()
        ok = img.load(filename)
        if not ok:
            raise IOError(f'Не удалось загрузить изображение: {filename}')
        self.set_image(img)

    def scale(self, w, h, keep_aspect=True):
        if self.original is None:
            return
        if keep_aspect:
            self.pixmap = QPixmap.fromImage(self.original).scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            self.pixmap = QPixmap.fromImage(self.original).scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    def get_pixmap(self):
        return self.pixmap

    def create_brush(self, tile=True):
        """Возвращает QBrush, созданную из текущего pixmap. Если pixmap пустой, возвращает None."""
        if self.pixmap is None:
            return None
        if tile:
            brush = QBrush(self.pixmap)
        else:
            brush = QBrush(self.pixmap)
        return brush


class PainterRaster(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Painter — растровые ресурсы и шаблонные кисти')
        self.resize(1000, 700)

        self.base_points = []  
        self.path = None       
        self.raster = RasterResource()
        self.show_raster = True
        self.fill_with_pattern = True

        self.pattern = self.make_default_pattern()
        self.pattern_resource = RasterResource(self.pattern.toImage())

        btn_layout = QHBoxLayout()
        btn_load = QPushButton('Загрузить растр...')
        btn_load.clicked.connect(self.load_raster)
        btn_scale = QPushButton('Масштабировать растр 50%')
        btn_scale.clicked.connect(self.scale_raster_half)
        btn_clear = QPushButton('Очистить точки')
        btn_clear.clicked.connect(self.clear_points)
        btn_build = QPushButton('Построить сплайн')
        btn_build.clicked.connect(self.build_spline)
        btn_fill = QPushButton('Fill shape with pattern')
        btn_fill.clicked.connect(self.fill_shape_with_pattern)

        self.chk_show_raster = QCheckBox('Показать растр')
        self.chk_show_raster.setChecked(True)
        self.chk_show_raster.stateChanged.connect(self.toggle_raster)

        self.chk_pattern = QCheckBox('Заливка шаблонной кистью')
        self.chk_pattern.setChecked(True)
        self.chk_pattern.stateChanged.connect(self.toggle_pattern)

        btn_layout.addWidget(btn_load)
        btn_layout.addWidget(btn_scale)
        btn_layout.addWidget(btn_clear)
        btn_layout.addWidget(btn_build)
        btn_layout.addWidget(btn_fill)
        btn_layout.addWidget(self.chk_show_raster)
        btn_layout.addWidget(self.chk_pattern)
        btn_layout.addStretch()

        instr = QLabel('ЛКМ: добавить точку. ПКМ по точке: удалить. Перетащить — переместить.')

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(10)
        self.slider.setMaximum(200)
        self.slider.setValue(100)
        self.slider.valueChanged.connect(self.on_slider_changed)
        lbl = QLabel('Масштаб растра (%)')

        layout = QVBoxLayout(self)
        layout.addLayout(btn_layout)
        layout.addWidget(instr)
        layout.addWidget(lbl)
        layout.addWidget(self.slider)

        self.drag_index = -1
        self._last_control_pairs = None

    def make_default_pattern(self):
        size = 16
        pm = QPixmap(size, size)
        pm.fill(QColor(255, 255, 255, 0))
        p = QPainter(pm)
        p.setPen(QPen(Qt.black, 1))
        p.drawLine(0, 0, size, size)
        p.drawLine(0, size, size, 0)
        p.end()
        return pm

    def toggle_raster(self, state):
        self.show_raster = state == Qt.Checked
        self.update()

    def toggle_pattern(self, state):
        self.fill_with_pattern = state == Qt.Checked
        self.update()

    def clear_points(self):
        self.base_points = []
        self.path = None
        self.update()

    def load_raster(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Открыть изображение', '', 'Images (*.png *.jpg *.bmp)')
        if not fname:
            return
        try:
            self.raster.load_from_file(fname)
            self.apply_slider_scale()
            self.update()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', str(e))

    def scale_raster_half(self):
        if self.raster.get_pixmap() is None:
            return
        pm = self.raster.get_pixmap()
        w = max(1, pm.width() // 2)
        h = max(1, pm.height() // 2)
        self.raster.scale(w, h, keep_aspect=False)
        self.update()

    def on_slider_changed(self, val):
        self.apply_slider_scale()
        self.update()

    def apply_slider_scale(self):
        if self.raster.original is None:
            return
        base = self.raster.original
        factor = self.slider.value() / 100.0
        w = max(1, int(base.width() * factor))
        h = max(1, int(base.height() * factor))
        self.raster.scale(w, h, keep_aspect=True)

    def mousePressEvent(self, event):
        p = event.pos()
        if event.button() == Qt.LeftButton:
            idx = self.find_nearest_point_index(p)
            if idx is not None and (self.base_points[idx] - p).manhattanLength() < 10:
                self.drag_index = idx
            else:
                self.base_points.append(QPointF(p))
                self.build_spline()
        elif event.button() == Qt.RightButton:
            idx = self.find_nearest_point_index(p)
            if idx is not None and (self.base_points[idx] - p).manhattanLength() < 10:
                del self.base_points[idx]
                self.build_spline()

    def mouseMoveEvent(self, event):
        if self.drag_index != -1:
            self.base_points[self.drag_index] = QPointF(event.pos())
            self.build_spline()

    def mouseReleaseEvent(self, event):
        self.drag_index = -1

    def find_nearest_point_index(self, pos):
        best_i = None
        best_d = None
        for i, pt in enumerate(self.base_points):
            d = (pt - pos).manhattanLength()
            if best_d is None or d < best_d:
                best_d = d
                best_i = i
        return best_i

    def build_spline(self):
        n = len(self.base_points)
        if n < 2:
            self.path = None
            self._last_control_pairs = None
            self.update()
            return
        P = self.base_points
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
        self.path = path
        self._last_control_pairs = control_pairs
        self.update()

    def fill_shape_with_pattern(self):
        if self.path is None:
            return
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), QColor(255, 255, 255))

        if self.show_raster and self.raster.get_pixmap() is not None:
            pm = self.raster.get_pixmap()
            x = (self.width() - pm.width())/2
            y = 80  
            painter.drawPixmap(int(x), int(y), pm)

        pen = QPen(Qt.black, 1)
        painter.setPen(pen)
        for pt in self.base_points:
            painter.drawEllipse(pt, 4, 4)

        if len(self.base_points) >= 2:
            pen = QPen(QColor(200, 200, 200), 1, Qt.DashLine)
            painter.setPen(pen)
            for i in range(len(self.base_points)-1):
                painter.drawLine(self.base_points[i], self.base_points[i+1])

        if self.path is not None:
            if self.fill_with_pattern:
                brush = self.pattern_resource.create_brush(tile=True)
                if brush is not None:
                    painter.save()
                    painter.setBrush(brush)
                    painter.setPen(Qt.NoPen)
                    painter.drawPath(self.path)
                    painter.restore()
            else:
                painter.save()
                painter.setBrush(QColor(200, 220, 255, 150))
                painter.setPen(Qt.NoPen)
                painter.drawPath(self.path)
                painter.restore()

            pen = QPen(QColor(10, 100, 200), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(self.path)

        if getattr(self, '_last_control_pairs', None) and self._last_control_pairs is not None:
            pen = QPen(QColor(180, 50, 50), 1, Qt.DashLine)
            painter.setPen(pen)
            for i, (C1, C2) in enumerate(self._last_control_pairs):
                painter.drawLine(self.base_points[i], C1)
                painter.drawLine(self.base_points[i+1], C2)
            pen = QPen(QColor(220, 120, 120), 1)
            painter.setPen(pen)
            for (C1, C2) in self._last_control_pairs:
                painter.drawEllipse(C1, 3, 3)
                painter.drawEllipse(C2, 3, 3)

    def load_star_preset(self):
        self.base_points = [QPointF(x, y) for x, y in [(200,150),(250,220),(320,240),(260,290),(280,360),(200,320),(120,360),(140,290),(80,240),(150,220),(200,150)]]
        self.build_spline()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = PainterRaster()

    btns = QHBoxLayout()
    btn_star = QPushButton('Звезда')
    btn_star.clicked.connect(w.load_star_preset)
    btns.addWidget(btn_star)
    w.layout().addLayout(btns)

    w.show()
    sys.exit(app.exec_())
