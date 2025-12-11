from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal


class PanelDreapta(QWidget):
    # Semnal emis când se apasă butonul manual
    start_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.title_label = QLabel("Bine ai venit la FACIEE!")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #333333;"
        )

        self.info_label = QLabel(
            "Pentru a începe aventura și a te înregistra,\nte rugăm să privești camera și să ZÂMBEȘTI! :)"
        )
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet(
            "font-size: 20px; color: #555555; margin-top: 20px;"
        )

        self.start_button = QPushButton("Sau apasă aici dacă nu poți zâmbi")
        self.start_button.setStyleSheet(
            """
            font-size: 14px; padding: 10px; background-color: #888; 
            color: white; border-radius: 5px; margin-top: 50px;
            """
        )
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addWidget(self.info_label)
        layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

        self.start_button.clicked.connect(self.start_clicked.emit)
