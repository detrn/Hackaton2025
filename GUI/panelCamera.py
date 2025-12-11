from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QFont, QPixmap, QImage
import cv2
import numpy as np


class OverlayLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        # Variabilă care decide dacă textul este vizibil
        self.show_text = True

    def hide_text(self):
        """Ascunde textul și forțează redesenarea."""
        self.show_text = False
        self.update()

    def paintEvent(self, event):
        # Dacă s-a cerut ascunderea textului, nu desenăm nimic
        if not self.show_text:
            return

        painter = QPainter(self)

        # Setăm fontul și culoarea
        font = QFont("Arial", 16, QFont.Bold)
        painter.setFont(font)
        painter.setPen(Qt.green)

        # Desenăm textul în partea de jos a ecranului
        w, h = self.width(), self.height()
        text = "ZÂMBEȘTE la cameră pentru a începe! :)"

        text_rect = QRect(0, h - 100, w, 50)
        painter.drawText(text_rect, Qt.AlignCenter, text)


class PanelCamera(QWidget):
    # Semnal emis când zâmbetul este detectat
    smile_detected = pyqtSignal()

    def __init__(self, camera, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.camera_label = QLabel(self)
        self.camera_label.setAlignment(Qt.AlignCenter)
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
        # Obținem cadrul brut
        raw_frame = self.camera.get_frame()

        if raw_frame is None:
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            self.display_image(blank)
            return

        frame_to_display = raw_frame

        # Procesăm doar dacă detecția este încă activă
        if self.detection_active:
            is_smiling, processed_frame = self.camera.detect_smile(raw_frame)
            frame_to_display = processed_frame

            if is_smiling:
                self.smile_counter += 1

                # Când atingem pragul de zâmbete consecutive
                if self.smile_counter >= self.smile_threshold:
                    self.detection_active = False

                    # --- MODIFICAREA ESTE AICI ---
                    # Ascundem textul de pe overlay
                    self.overlay.hide_text()

                    # Emitem semnalul pentru a schimba panoul din dreapta
                    self.smile_detected.emit()
            else:
                self.smile_counter = 0

                # Dacă detecția NU mai e activă, afișăm cadrul curat (raw_frame),
        # fără pătrățele verzi/albastre pe față.

        self.display_image(frame_to_display)

    def display_image(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qimage = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(qimage)
        self.camera_label.setPixmap(pixmap)