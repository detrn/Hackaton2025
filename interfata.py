import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QSplitter, QTextEdit
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QSizePolicy
import os
os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera în panelul stâng")

        # --- CAMERA ---
        self.cap = cv2.VideoCapture(0)  # 0 = camera default
        self.camera_label = QLabel()
        self.camera_label.setStyleSheet("background-color: black;")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Timer care actualizează frame-ul camerei
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # ~33 FPS (30 ms)

        # --- PANEL DREAPTA ---
        right_panel = QTextEdit()
        right_panel.setText("Panel dreapta (1/3)")
        right_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.camera_label.setMinimumWidth(200)  # limita minimă
        right_panel.setMinimumWidth(300)

        # --- SPLITTER CU RAPORT 1:3 ---
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.camera_label)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)  # panelul stânga = 1 parte
        splitter.setStretchFactor(1, 3)  # panelul dreapta = 3 părți

        splitter.setSizes([300, 900])   # raport stânga:dreapta = 1:3


        # Setăm layout-ul
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        container.setLayout(layout)

        self.setCentralWidget(container)

    def update_frame(self):
        """Ia frame din OpenCV și îl pune în QLabel."""
        ret, frame = self.cap.read()
        if not ret:
            return

        # OpenCV folosește BGR → convertim în RGB pentru Qt
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convertim într-un QImage
        h, w, ch = frame.shape
        bytes_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_line, QImage.Format_RGB888)

        # Punem imaginea în QLabel
        self.camera_label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        """Oprire camera când fereastra se închide."""
        self.cap.release()
        event.accept()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()