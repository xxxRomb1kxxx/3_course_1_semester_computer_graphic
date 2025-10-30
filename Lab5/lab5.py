import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QComboBox, QSlider
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class BMViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BMViewer — режимы масштабирования BMP")
        self.resize(900, 700)

        self.image_label = QLabel(alignment=Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #ddd; border: 1px solid gray;")
        self.image_label.setMinimumSize(600, 400)


        self.btn_load = QPushButton("Загрузить BMP")
        self.btn_load.clicked.connect(self.load_image)

        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(10, 300)
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(self.update_scaled_image)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["По соседним", "Линейная интерполяция", "Сплайновая интерполяция"])
        self.mode_combo.currentIndexChanged.connect(self.update_scaled_image)

        controls = QHBoxLayout()
        controls.addWidget(self.btn_load)
        controls.addWidget(self.mode_combo)
        controls.addWidget(QLabel("Масштаб (%)"))
        controls.addWidget(self.scale_slider)

        layout = QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(self.image_label)

        self.original_image = None

    def load_image(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Открыть BMP", "", "BMP files (*.bmp)"
        )
        if not fname:
            return
        self.original_image = QImage(fname)
        self.update_scaled_image()

    def update_scaled_image(self):
        if self.original_image is None:
            return
        factor = self.scale_slider.value() / 100.0
        w = max(1, int(self.original_image.width() * factor))
        h = max(1, int(self.original_image.height() * factor))

        mode = self.mode_combo.currentText()
        if mode == "По соседним":
            transform_mode = Qt.FastTransformation  
            image_scaled = self.original_image.scaled(w, h, Qt.IgnoreAspectRatio, transform_mode)
        elif mode == "Линейная интерполяция":
            image_scaled = self.original_image.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        else:
            image_scaled = self.original_image.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

        self.image_label.setPixmap(QPixmap.fromImage(image_scaled))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = BMViewer()
    viewer.show()
    sys.exit(app.exec_())
