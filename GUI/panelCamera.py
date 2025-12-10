from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QFont, QPixmap, QImage
import cv2
import numpy as np


from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter, QPen, QFont
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import Qt, QRectF
import math

class OverlayLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Timer pentru animație
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(30)  # ~30 FPS
        self.rotation_angle = 0
        self.frame_count = 0  # pentru animație

    def on_timer(self):
        self.frame_count += 1
        self.rotation_angle += 16  # un pas de rotație
        if self.rotation_angle >= 16 * 360:
            self.rotation_angle = 0
        self.update()

    def update_animation(self):
        self.frame_count += 1
        self.rotation_angle += 16  # rotim puțin la fiecare frame
        if self.rotation_angle >= 16 * 360:
            self.rotation_angle = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Cerc alb în partea superioară
        pen = QPen(Qt.white, 4)
        painter.setPen(pen)
        w, h = self.width(), self.height()
        radius = min(w, h) // 6
        center_x, center_y = w // 2, 400
        rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # Unghiurile în PyQt se dau în 1/16 grade!
        # 360° = 16*360 = 5760
        # desenăm 4 segmente a câte 90° fiecare
        for i in range(4):
            start_angle = self.rotation_angle + i * 90 * 16
            span_angle = 60 * 16
            painter.drawArc(rect, start_angle, span_angle)
        # Font care pulsează
        pulse_size = 12 + 4 * math.sin(self.frame_count * 0.1)  # între 8 și 16 px
        font = QFont("Arial", int(pulse_size))
        painter.setFont(font)
        painter.setPen(Qt.white)

        # Text sub cerc
        text = "Poziționează fața în interiorul cercului și apasă butonul pentru a începe!"
        text_y = 600 + radius + 20
        painter.drawText(10, text_y, w - 20, 60, Qt.AlignHCenter | Qt.TextWordWrap, text)

class PanelCamera(QWidget):
    def __init__(self, camera, parent=None):
        super().__init__(parent)
        self.camera = camera

        # QLabel pentru cameră
        self.camera_label = QLabel(self)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("background-color: black;")
        self.camera_label.setScaledContents(True)

        # Overlay transparent peste cameră
        self.overlay = OverlayLabel(self)

    def resizeEvent(self, event):
        # Ambele ocupă tot spațiul
        self.camera_label.setGeometry(0, 0, self.width(), self.height())
        self.overlay.setGeometry(0, 0, self.width(), self.height())

    def update_frame(self):
        frame = self.camera.get_frame()
        if frame is None:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimage = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage).scaled(
            self.camera_label.width(),
            self.camera_label.height(),
            Qt.KeepAspectRatio,
        )
        self.camera_label.setPixmap(pixmap)