import sys
import cv2
import numpy as np
import requests
import random
import time
import subprocess  # <--- NECESAR PENTRU LANSAREA JOCURILOR

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout,
    QPushButton, QHBoxLayout, QMessageBox, QStackedWidget, QLineEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QFont, QPixmap, QImage, QBrush


# ==========================================
# BACKEND - GENERATOR AVATAR
# ==========================================
class AvatarGenerator:
    @staticmethod
    def generate(seed=None):
        if seed is None:
            seed = random.randint(1, 999999)

        stil = "avataaars"
        url = f"https://api.dicebear.com/9.x/{stil}/png?seed={seed}&backgroundColor=transparent"

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            image = QImage()
            image.loadFromData(response.content)

            size = 400
            image = image.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            out_img = QImage(size, size, QImage.Format_ARGB32)
            out_img.fill(Qt.transparent)

            brush = QBrush(image)
            painter = QPainter(out_img)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(brush)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, size, size)
            painter.end()

            return QPixmap.fromImage(out_img)

        except Exception as e:
            print(f"Eroare retea: {e}")
            return None


# ==========================================
# BACKEND - CAMERA
# ==========================================
class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

    def get_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return cv2.flip(frame, 1)
        return None

    def detect_smile(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(60, 60))
        is_smiling = False

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            smiles = self.smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=25, minSize=(25, 25))

            if len(smiles) > 0:
                is_smiling = True
                for (sx, sy, sw, sh) in smiles:
                    cv2.rectangle(frame, (x + sx, y + sy), (x + sx + sw, y + sy + sh), (0, 255, 0), 1)

        return is_smiling, frame

    def release(self):
        if self.cap.isOpened():
            self.cap.release()


# ==========================================
# GUI - PARTEA 1: CAMERA
# ==========================================
class OverlayLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.rotation_angle = 0
        self.frame_count = 0
        self.status_text = "ZÂMBEȘTE PENTRU A ÎNCEPE!"
        self.status_color = Qt.white

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)

    def update_animation(self):
        self.frame_count += 1
        self.rotation_angle = (self.rotation_angle + 2) % 360
        self.update()

    def set_status(self, text, color):
        self.status_text = text
        self.status_color = color

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        radius = min(w, h) // 4
        center_x, center_y = w // 2, h // 2

        pen = QPen(self.status_color, 6)
        painter.setPen(pen)
        rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)

        for i in range(3):
            start = (self.rotation_angle * 16) + (i * 120 * 16)
            painter.drawArc(rect, start, 60 * 16)

        font = QFont("Arial", 20, QFont.Bold)
        painter.setFont(font)
        painter.setPen(self.status_color)
        text_rect = QRectF(0, center_y + radius + 20, w, 100)
        painter.drawText(text_rect, Qt.AlignCenter, self.status_text)


class PanelCamera(QWidget):
    smile_confirmed = pyqtSignal()

    def __init__(self, camera, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.camera_label = QLabel(self)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("background-color: #1e1e1e;")

        self.overlay = OverlayLabel(self)
        self.smile_counter = 0
        self.SMILE_THRESHOLD = 15

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def resizeEvent(self, event):
        self.camera_label.setGeometry(0, 0, self.width(), self.height())
        self.overlay.setGeometry(0, 0, self.width(), self.height())

    def update_frame(self):
        frame = self.camera.get_frame()
        if frame is not None:
            smiling, debug_frame = self.camera.detect_smile(frame)

            if smiling:
                self.smile_counter += 1
                self.overlay.set_status(f"MENȚINE... {self.smile_counter}", Qt.green)
            else:
                self.smile_counter = max(0, self.smile_counter - 1)
                self.overlay.set_status("TE ROG SĂ ZÂMBEȘTI!", Qt.white)

            rgb_frame = cv2.cvtColor(debug_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            q_img = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(q_img).scaled(
                self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))

            if self.smile_counter >= self.SMILE_THRESHOLD:
                self.timer.stop()
                self.smile_confirmed.emit()


# ==========================================
# GUI - PARTEA 2: AVATAR
# ==========================================
class PanelAvatar(QWidget):
    go_next = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()

        self.lbl_title = QLabel("AVATARUL TĂU ONLINE")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setFont(QFont("Arial", 24, QFont.Bold))

        self.lbl_image = QLabel()
        self.lbl_image.setAlignment(Qt.AlignCenter)
        self.lbl_image.setMinimumSize(400, 400)

        btn_layout = QHBoxLayout()

        self.btn_regen = QPushButton("Alt Avatar")
        self.btn_regen.setStyleSheet(
            "background-color: #3498db; color: white; padding: 15px; border-radius: 8px; font-size: 16px;")
        self.btn_regen.clicked.connect(self.load_new_avatar)

        self.btn_next = QPushButton("Continuă ->")
        self.btn_next.setStyleSheet(
            "background-color: #2ecc71; color: white; padding: 15px; border-radius: 8px; font-size: 16px; font-weight: bold;")
        self.btn_next.clicked.connect(self.go_next.emit)

        btn_layout.addWidget(self.btn_regen)
        btn_layout.addWidget(self.btn_next)

        layout.addWidget(self.lbl_title)
        layout.addStretch()
        layout.addWidget(self.lbl_image)
        layout.addStretch()
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.current_pixmap = None  # Stocăm imaginea curentă

    def load_new_avatar(self):
        self.lbl_title.setText("Se descarcă...")
        QApplication.processEvents()
        pixmap = AvatarGenerator.generate()
        if pixmap:
            self.current_pixmap = pixmap  # Salvăm imaginea
            self.lbl_image.setPixmap(pixmap)
            self.lbl_title.setText("AVATARUL TĂU ONLINE")
        else:
            self.lbl_title.setText("Eroare la descărcare")


# ==========================================
# GUI - PARTEA 3: MENIU JOCURI (MODIFICAT PENTRU AVATAR COLȚ)
# ==========================================
class PanelMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #ecf0f1;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 30, 50, 50)

        # --- HEADER NOU (Titlu + Avatar Colț) ---
        header_layout = QHBoxLayout()

        # Titlu (Stânga)
        title = QLabel("BINE AI VENIT, STUDENTULE!")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")

        # Avatar Colț (Dreapta)
        self.lbl_avatar_corner = QLabel()
        self.lbl_avatar_corner.setFixedSize(120, 120)
        self.lbl_avatar_corner.setScaledContents(True)
        # Un mic stil pentru chenar rotund
        self.lbl_avatar_corner.setStyleSheet("""
            border: 3px solid #3498db;
            border-radius: 60px; 
            background-color: white;
        """)

        header_layout.addWidget(title)
        header_layout.addStretch()  # Împinge avatarul în dreapta
        header_layout.addWidget(self.lbl_avatar_corner)

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(40)
        # ----------------------------------------

        # Input Nume
        lbl_nume = QLabel("Cum te cheamă?")
        lbl_nume.setFont(QFont("Arial", 14))

        self.input_nume = QLineEdit()
        self.input_nume.setPlaceholderText("Introdu numele tău aici...")
        self.input_nume.setStyleSheet("""
            QLineEdit { padding: 15px; font-size: 18px; border: 2px solid #bdc3c7; border-radius: 10px; background-color: white; }
            QLineEdit:focus { border: 2px solid #3498db; }
        """)

        main_layout.addWidget(lbl_nume)
        main_layout.addWidget(self.input_nume)
        main_layout.addSpacing(40)

        # Sectiune Jocuri
        lbl_alege = QLabel("ALEGE SPECIALIZAREA:")
        lbl_alege.setAlignment(Qt.AlignCenter)
        lbl_alege.setFont(QFont("Arial", 18, QFont.Bold))
        main_layout.addWidget(lbl_alege)
        main_layout.addSpacing(20)

        btn_layout = QHBoxLayout()

        self.btn_telecom = self.create_game_btn("📡 TELECOM", "#8e44ad")
        self.btn_hardware = self.create_game_btn("🔌 HARDWARE", "#e67e22")
        self.btn_software = self.create_game_btn("💻 SOFTWARE", "#2980b9")

        # --- CONECTARE BUTOANE ---
        self.btn_telecom.clicked.connect(lambda: self.start_game("Telecomunicații"))
        self.btn_hardware.clicked.connect(lambda: self.start_game("Hardware"))
        self.btn_software.clicked.connect(lambda: self.start_game("Software"))

        btn_layout.addWidget(self.btn_telecom)
        btn_layout.addWidget(self.btn_hardware)
        btn_layout.addWidget(self.btn_software)

        main_layout.addLayout(btn_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def create_game_btn(self, text, color):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.setStyleSheet(f"""
            QPushButton {{ background-color: {color}; color: white; font-size: 20px; font-weight: bold; border-radius: 15px; padding: 20px; }}
            QPushButton:hover {{ background-color: {color}dd; margin-top: -5px; }}
        """)
        return btn

    # --- FUNCȚIE NOUĂ PENTRU PRIMIREA IMAGINII ---
    def set_avatar_image(self, pixmap):
        if pixmap:
            # Scalăm imaginea să se potrivească în colț (120x120)
            scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_avatar_corner.setPixmap(scaled_pixmap)

    # ---------------------------------------------

    def start_game(self, game_name):
        nume = self.input_nume.text().strip()
        if not nume:
            QMessageBox.warning(self, "Atenție", "Te rog să introduci numele tău înainte de a începe!")
            self.input_nume.setFocus()
            return

        # --- LANSARE JOCURI CA PROCESE SEPARATE ---
        if game_name == "Hardware":
            try:
                # Lansăm jocul de hardware (asigură-te că joc_iec.py e în folder)
                subprocess.Popen([sys.executable, "joc_iec.py"])
            except Exception as e:
                QMessageBox.critical(self, "Eroare", f"Nu s-a putut lansa jocul Hardware: {e}")

        elif game_name == "Telecomunicații":
            try:
                # Lansăm jocul de semnale (asigură-te că JocIETTI.py e în folder)
                subprocess.Popen([sys.executable, "JocIETTI.py"])
            except Exception as e:
                QMessageBox.critical(self, "Eroare", f"Nu s-a putut lansa jocul Telecom: {e}")

        elif game_name == "Software":
            QMessageBox.information(self, "Info", "Acest joc este în dezvoltare!")


# ==========================================
# MAIN WINDOW - ORCHESTRATOR
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicație Facultate - IETTI")
        self.resize(1000, 800)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 1. Ecran Cameră
        self.camera = Camera()
        self.panel_camera = PanelCamera(self.camera)
        self.panel_camera.smile_confirmed.connect(self.go_to_avatar)

        # 2. Ecran Avatar
        self.panel_avatar = PanelAvatar()
        self.panel_avatar.go_next.connect(self.go_to_menu)

        # 3. Ecran Meniu
        self.panel_menu = PanelMenu()

        self.stack.addWidget(self.panel_camera)  # Index 0
        self.stack.addWidget(self.panel_avatar)  # Index 1
        self.stack.addWidget(self.panel_menu)  # Index 2

    def go_to_avatar(self):
        self.camera.release()
        self.panel_avatar.load_new_avatar()
        self.stack.setCurrentIndex(1)

    def go_to_menu(self):
        # --- TRANSFERUL IMAGINII ---
        # Luăm imaginea curentă din panoul Avatar
        avatar_pixmap = self.panel_avatar.current_pixmap
        # O trimitem către panoul Meniu
        self.panel_menu.set_avatar_image(avatar_pixmap)
        # ---------------------------

        self.stack.setCurrentIndex(2)

    def closeEvent(self, event):
        self.camera.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())