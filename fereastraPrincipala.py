# main.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QVBoxLayout, QWidget
)
from PyQt6.QtCore import Qt, QTimer
from camera import Camera
from GUI.panelCamera import PanelCamera
from GUI.panelDreapta import PanelDreapta
from GUI.panelJocuri import PanelJocuri  # Panelul jocuri modular

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicatie facultate")

        # --- Camera ---
        self.camera = Camera()
        self.camera_panel = PanelCamera(self.camera)

        # --- Panel dreapta modular ---
        self.right_panel = PanelDreapta()

        # Conectăm butonul de start la metoda de înlocuire
        self.right_panel.start_button.clicked.connect(self.load_game_panel)

        # --- Splitter 1:3 ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.camera_panel)
        self.splitter.addWidget(self.right_panel)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setSizes([400, 1200])

        # Layout central
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.splitter)
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Timer pentru refresh camera + animații overlay
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(30)  # ~33 FPS

    def refresh(self):
        """Actualizează frame-ul camerei și repaint overlay"""
        self.camera_panel.update_frame()
        self.camera_panel.overlay.update()

    def load_game_panel(self):
        """Înlocuiește panelul dreapta cu panelul jocuri păstrând dimensiunea camerei"""
        game_panel = PanelJocuri()  # creează panelul jocuri

        # Înlocuiește widget-ul din splitter
        self.splitter.replaceWidget(1, game_panel)

        # Șterge vechiul panel din memorie
        self.right_panel.setParent(None)
        self.right_panel.deleteLater()

        # Actualizează referința
        self.right_panel = game_panel

        # Fixăm dimensiunea splitter-ului pentru a păstra proporția
        self.splitter.setStretchFactor(0, 1)  # PanelCamera rămâne 1/4 din spațiu
        self.splitter.setStretchFactor(1, 3)  # PanelJocuri ocupă restul
        self.splitter.setSizes([self.camera_panel.width(), self.width() - self.camera_panel.width()])

    def closeEvent(self, event):
        """Eliberează resursele camerei la închidere"""
        self.camera.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
