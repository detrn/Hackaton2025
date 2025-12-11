from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QWidget


class Color(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        # PyQt6 folosește ColorRole.Window
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)
