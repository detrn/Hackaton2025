# GUI/panelJocuri.py
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QSpacerItem, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter
import random
import sys

# --- Clasa LoadingWheel ---
class LoadingWheel(QWidget):
    """Roată de încărcare animată simplă"""
    def __init__(self, parent=None, radius=25, segments=12):
        super().__init__(parent)
        self.radius = radius
        self.segments = segments
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        self.timer.start(50)
        self.angle = 0

    def rotate(self):
        self.angle += 30
        if self.angle >= 360:
            self.angle = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        for i in range(self.segments):
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.gray)
            opacity = (i + self.angle // 30) % self.segments / self.segments
            painter.setOpacity(opacity)
            painter.drawEllipse(cx - self.radius, cy - self.radius, self.radius * 2, self.radius * 2)

# --- Clasa PanelJocuri ---
class PanelJocuri(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_data = {}

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- Spacer sus ---
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # --- Label instrucțiuni ---
        label_instr = QLabel(
            "Introdu numele și lasă programul să ghicească specializarea care ți se potrivește:"
        )
        label_instr.setWordWrap(True)
        label_instr.setAlignment(Qt.AlignCenter)
        label_instr.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label_instr)

        # --- Input nume ---
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nume student")
        self.name_input.setFixedHeight(40)
        self.name_input.setFixedWidth(250)
        self.name_input.setStyleSheet("""
            font-size: 14px;
            padding: 6px 10px;
            border: 2px solid #4CAF50;
            border-radius: 8px;
        """)
        layout.addWidget(self.name_input, alignment=Qt.AlignCenter)

        # --- Buton start ---
        self.start_button = QPushButton("Testează-ți aptitudinile!")
        self.start_button.setFixedHeight(50)
        self.start_button.setFixedWidth(200)
        self.start_button.setStyleSheet("""
            font-size: 14px;
            padding: 6px;
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
        """)
        self.start_button.clicked.connect(self.start_test)
        layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        # --- Roată de încărcare ---
        self.loading_wheel = LoadingWheel()
        self.loading_wheel.setFixedSize(60, 60)
        self.loading_wheel.hide()
        layout.addWidget(self.loading_wheel, alignment=Qt.AlignCenter)

        # --- Rezultat ---
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        self.result_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.result_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2E4053;
            padding: 10px;
        """)
        layout.addWidget(self.result_label)

        # --- Text explicativ ---
        self.explanation_label = QLabel("")
        self.explanation_label.setAlignment(Qt.AlignCenter)
        self.explanation_label.setWordWrap(True)
        self.explanation_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.explanation_label.setStyleSheet("""
            font-size: 20px;
            color: #34495E;
            padding: 5px;
        """)
        layout.addWidget(self.explanation_label)

        # --- Buton suplimentar ---
        self.extra_button = QPushButton(
            "Testează-ți aptitudinile în domeniul\nvisurilor tale prin jocul nostru"
        )
        self.extra_button.setMinimumHeight(70)
        self.extra_button.setMinimumWidth(320)
        self.extra_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px 20px;
                background-color: #FF5733;
                color: white;
                border-radius: 8px;
                text-align: center;
            }
        """)
        self.extra_button.hide()
        layout.addWidget(self.extra_button, alignment=Qt.AlignCenter)

        # --- Spacer jos ---
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)

        # Mesaje predefinite
        self.specializari_text = {
            "CTI": "Pari un tip pragmatic, ce încearcă să rezolve problemele în stil practic și pentru care programarea nu e o problemă. De aceea am ales specializarea CTI.",
            "IEC": "Ai o gândire analitică și ești orientat spre inginerie și electricitate. Programarea e doar un instrument pentru ideile tale. Am ales IEC.",
            "IETTI": "Ești curios și inventiv, gata să explorezi tehnologia informației și telecomunicații. Specializarea ta este IETTI.",
            "AIA": "Ai simț estetic și logic, combinând arta cu inteligența artificială. Ai nevoie de provocări creative – AIA e perfect pentru tine.",
            "IE": "Ești orientat spre inginerie aplicată, cu spirit practic și determinare. Programarea te ajută să-ți atingi scopurile. Specializarea ta: IE."
        }

    def start_test(self):
        name = self.name_input.text().strip()
        if not name:
            self.result_label.setText("Trebuie să introduci un nume!")
            return

        self.user_data['nume'] = name
        self.loading_wheel.show()
        self.result_label.setText("")
        self.explanation_label.setText("")
        self.extra_button.hide()

        QTimer.singleShot(2000, self.show_result)

    def show_result(self):
        self.loading_wheel.hide()
        specializare = random.choice(list(self.specializari_text.keys()))
        mesaj = self.specializari_text[specializare]

        # Corect: text complet cu nume și specializare
        self.result_label.setText(f"{self.user_data['nume']}, specializarea ta este: {specializare}")
        self.explanation_label.setText(mesaj)
        self.extra_button.show()

# --- TESTARE PANEL INDEPENDENTĂ ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = PanelJocuri()
    panel.setWindowTitle("Panel Jocuri")
    panel.resize(500, 600)
    panel.show()
    sys.exit(app.exec())
