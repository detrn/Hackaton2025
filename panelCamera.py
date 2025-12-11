from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QFont, QPixmap, QImage
import cv2
import numpy as np


class OverlayLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.show_text = True  # Variabilă care decide dacă textul este vizibil

    def hide_text(self):
        """Ascunde textul și forțează redesenarea."""
        self.show_text = False
        self.update()

    def paintEvent(self, event):
        if not self.show_text:
            return

        painter = QPainter(self)
        font = QFont("Arial", 16, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(Qt.GlobalColor.green)

        w, h = self.width(), self.height()
        text = "ZÂMBEȘTE la cameră pentru a începe! :)"

        text_rect = QRect(0, h - 100, w, 50)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)


class PanelCamera(QWidget):
    smile_detected = pyqtSignal()  # Semnal emis când zâmbetul este detectat

    def __init__(self, camera, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.camera_label = QLabel(self)
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("background-color: black;")
        self.camera_label.setScaledContents(True)

        self.overlay = OverlayLabel(self)

        # Variabile pentru detectia zambetului
        self.smile_counter = 0
        self.smile_threshold = 10  # Aprox 0.3 - 0.5 secunde
        self.detection_active = True

    def resizeEvent(self, event):
        self.camera_label.setGeometry(0, 0, self.width(), self.height())
        self.overlay.setGeometry(0, 0, self.width(), self.height())

    def update_frame(self):
        raw_frame = self.camera.get_frame()

        if raw_frame is None:
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            self.display_image(blank)
            return

        frame_to_display = raw_frame

        if self.detection_active:
            is_smiling, processed_frame = self.camera.detect_smile(raw_frame)
            frame_to_display = processed_frame

            if is_smiling:
                self.smile_counter += 1

                if self.smile_counter >= self.smile_threshold:
                    self.detection_active = False
                    self.overlay.hide_text()
                    self.smile_detected.emit()
            else:
                self.smile_counter = 0

        self.display_image(frame_to_display)

    def display_image(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qimage = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

        pixmap = QPixmap.fromImage(qimage)
        self.camera_label.setPixmap(pixmap)
