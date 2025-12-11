import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer

from camera import Camera
from Hackaton2025.panelCamera import PanelCamera
from Hackaton2025.panelDreapta import PanelDreapta
from Hackaton2025.panelJocuri import PanelJocuri


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicatie facultate")
        self.resize(1200, 800)  # O dimensiune de start mai generoasă

        # --- Camera ---
        self.camera = Camera()
        self.camera_panel = PanelCamera(self.camera)

        # Conectăm semnalul de zâmbet
        self.camera_panel.smile_detected.connect(self.load_game_panel)

        # --- Panel dreapta modular (Start) ---
        self.right_panel = PanelDreapta()
        # Conectăm și butonul manual (backup)
        self.right_panel.start_clicked.connect(self.load_game_panel)

        # --- Splitter ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.camera_panel)
        self.splitter.addWidget(self.right_panel)

        # MODIFICARE LĂȚIME:
        self.splitter.setStretchFactor(0, 4)  # Camera
        self.splitter.setStretchFactor(1, 5)  # Panel Dreapta

        # Dimensiuni inițiale
        self.splitter.setSizes([500, 700])

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.splitter)
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Timer refresh
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(30)

    def refresh(self):
        self.camera_panel.update_frame()
        self.camera_panel.overlay.update()

    def load_game_panel(self):
        # Verificăm dacă nu cumva am încărcat deja panelul de jocuri
        if isinstance(self.right_panel, PanelJocuri):
            return

        print("Trecere la Panel Jocuri...")
        game_panel = PanelJocuri()
        self.splitter.replaceWidget(1, game_panel)
        game_panel.close_main_window.connect(self.close)

        self.right_panel.setParent(None)
        self.right_panel.deleteLater()
        self.right_panel = game_panel

        # Păstrăm proporțiile și după schimbare
        self.splitter.setSizes([500, self.width() - 500])


    def closeEvent(self, event):
        self.camera.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
