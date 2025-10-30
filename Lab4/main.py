import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QPixmap, QImage, QBrush, QPainter
from PyQt6.QtCore import Qt
import cv2
import numpy as np


class RasterImage:
    """Класс для работы с растровыми изображениями"""
    def __init__(self, path=None, width=300, height=300, color=(255, 255, 255)):
        if path:
            # пробуем загрузить картинку
            img = cv2.imread(path)
            if img is None:
                # если не удалось — создаём пустой фон
                img = np.full((height, width, 3), color, dtype=np.uint8)
            self.image = img
        else:
            # если путь не задан — создаём пустой фон
            self.image = np.full((height, width, 3), color, dtype=np.uint8)

    def to_qpixmap(self):
        """Преобразуем NumPy → QPixmap"""
        h, w, ch = self.image.shape
        bytes_per_line = ch * w
        qimg = QImage(self.image.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
        return QPixmap.fromImage(qimg)


class RasterWidget(QWidget):
    def __init__(self, raster_path=None):
        super().__init__()
        self.setWindowTitle("Растровое изображение и кисть")
        self.setGeometry(100, 100, 650, 700)

        layout = QVBoxLayout()
        self.label = QLabel(self)
        layout.addWidget(self.label)
        self.setLayout(layout)

        # 1. Загружаем растровое изображение
        raster = RasterImage(raster_path)
        pixmap_raster = raster.to_qpixmap()

        # 2. Создаем шаблон кисти (растровый узор)
        brush_pixmap = QPixmap(20, 20)
        brush_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(brush_pixmap)
        painter.setBrush(Qt.GlobalColor.red)
        painter.drawEllipse(2, 2, 8, 8)
        painter.setBrush(Qt.GlobalColor.blue)
        painter.drawRect(10, 10, 8, 8)
        painter.end()

        brush = QBrush(brush_pixmap)

        # 3. Рисуем фигуру с заливкой этой кистью
        filled = QPixmap(300, 300)
        filled.fill(Qt.GlobalColor.white)

        painter = QPainter(filled)
        painter.setBrush(brush)
        painter.drawEllipse(50, 50, 200, 200)  # круг с заливкой кистью
        painter.end()

        # 4. Собираем всё в одно изображение
        final_pixmap = QPixmap(600, 650)
        final_pixmap.fill(Qt.GlobalColor.white)

        painter = QPainter(final_pixmap)
        painter.drawPixmap(0, 0, pixmap_raster.scaled(600, 300, Qt.AspectRatioMode.KeepAspectRatio))
        painter.drawPixmap(0, 320, filled)
        painter.end()

        self.label.setPixmap(final_pixmap)


def main():
    app = QApplication(sys.argv)

    # укажи путь к изображению (например, PNG/JPG)
    path = "example.png"   # <-- замени на свой файл
    window = RasterWidget(path)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
