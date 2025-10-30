import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QScrollArea, QFileDialog, QToolBar,
    QComboBox, QStatusBar, QMessageBox
)
from PyQt6.QtGui import QPixmap, QImage, QAction, QTransform
from PyQt6.QtCore import Qt, QSize


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Viewer with Scaling Modes")
        self.setGeometry(100, 100, 800, 600)

        self.scale_factor = 1.0
        self.current_pixmap = None
        self.scaling_mode = Qt.TransformationMode.FastTransformation

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        self.setCentralWidget(self.scroll_area)

        self.create_toolbar()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_image)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["Nearest Neighbor", "Linear Interpolation", "Spline Interpolation"])
        self.scale_combo.currentIndexChanged.connect(self.set_scaling_mode)
        toolbar.addWidget(self.scale_combo)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "BMP Images (*.bmp);;All Files (*)"
        )
        if file_path:
            image = QImage(file_path)
            if image.isNull():
                QMessageBox.warning(self, "Error", "Cannot open image!")
                return
            self.current_pixmap = QPixmap.fromImage(image)
            self.scale_factor = 1.0
            self.update_image()

    def set_scaling_mode(self, index):
        if index == 0:
            self.scaling_mode = Qt.TransformationMode.FastTransformation
        elif index == 1:
            self.scaling_mode = Qt.TransformationMode.SmoothTransformation
        elif index == 2:
            # Используем SmoothTransformation как приближение для сплайновой интерполяции
            self.scaling_mode = Qt.TransformationMode.SmoothTransformation
        self.update_image()

    def update_image(self):
        if self.current_pixmap:
            scaled_pixmap = self.current_pixmap.scaled(
                self.current_pixmap.size() * self.scale_factor,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                self.scaling_mode
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.status_bar.showMessage(f"Scale: {self.scale_factor:.2f}")

    def wheelEvent(self, event):
        if self.current_pixmap:
            delta = event.angleDelta().y()
            if delta > 0:
                self.scale_factor *= 1.1
            else:
                self.scale_factor /= 1.1
            self.update_image()


def main():
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
