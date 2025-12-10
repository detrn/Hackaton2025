# GUI/panelDreapta.py
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal

class PanelDreapta(QWidget):
    start_clicked = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

        # Titlu mare
        self.title_label = QLabel("Ești gata să devii noul student al FACIEE?")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)  # ca textul să se împacheteze pe mai multe rânduri
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333333;
        """)

        # Buton pentru începerea aventurii
        self.start_button = QPushButton("Începe aventura!")
        self.start_button.setStyleSheet("""
            font-size: 18px;
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
        """)

        # Layout vertical
        layout = QVBoxLayout()
        layout.addStretch()  # spațiu de sus
        layout.addWidget(self.title_label)
        layout.addSpacing(20)  # spațiu între titlu și buton
        layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        layout.addStretch()  # spațiu jos
        self.setLayout(layout)
        self.start_button.clicked.connect(self.start_clicked.emit)
