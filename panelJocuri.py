import sys
import os
import csv
import random
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QPixmap, QBrush

# ==========================
# Loading Wheel (Animație)
# ==========================
class LoadingWheel(QWidget):
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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        for i in range(self.segments):
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(Qt.GlobalColor.gray))
            opacity = (i + self.angle // 30) % self.segments / self.segments
            painter.setOpacity(opacity)
            painter.drawEllipse(cx - self.radius, cy - self.radius,
                                self.radius * 2, self.radius * 2)

# ==========================
# Avatar Generator import
# ==========================
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

try:
    from avatar_generator import AvatarGenerator
except ImportError:
    class AvatarGenerator:
        @staticmethod
        def generate():
            return None, "asset/avatar_default.png"

# ==========================
# PANEL JOCURI COMPLET
# ==========================
class PanelJocuri(QWidget):
    close_main_window = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.user_data = {"nume": "", "specializare": "", "avatar": ""}

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        label_instr = QLabel("Introdu numele și lasă programul să ghicească specializarea:")
        label_instr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_instr.setWordWrap(True)
        label_instr.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label_instr)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nume student")
        self.name_input.setFixedHeight(40)
        self.name_input.setFixedWidth(250)
        self.name_input.setStyleSheet("""
            font-size: 14px; padding: 6px;
            border: 2px solid #4CAF50; border-radius: 8px;
        """)
        layout.addWidget(self.name_input, alignment=Qt.AlignmentFlag.AlignCenter)

        self.start_button = QPushButton("Generează Avatar & Profil")
        self.start_button.setFixedHeight(50)
        self.start_button.setFixedWidth(250)
        self.start_button.setStyleSheet("""
            font-size: 14px; background-color: #4CAF50;
            color: white; border-radius: 8px;
        """)
        self.start_button.clicked.connect(self.start_test)
        layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.loading_wheel = LoadingWheel()
        self.loading_wheel.setFixedSize(60, 60)
        self.loading_wheel.hide()
        layout.addWidget(self.loading_wheel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.avatar_label = QLabel()
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2E4053;")
        layout.addWidget(self.result_label)

        self.explanation_label = QLabel("")
        self.explanation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.explanation_label.setWordWrap(True)
        self.explanation_label.setStyleSheet("font-size: 20px; color: #34495E;")
        layout.addWidget(self.explanation_label)

        self.extra_button = QPushButton("Start Joc")
        self.extra_button.setMinimumHeight(60)
        self.extra_button.setStyleSheet("""
            font-size: 14px; background-color: #FF5733;
            color: white; border-radius: 8px;
        """)
        self.extra_button.hide()
        self.extra_button.clicked.connect(self.start_joc_simplu)
        layout.addWidget(self.extra_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.setLayout(layout)

        self.specializari_text = {
            "CTI": "Pari un tip pragmatic – deci ai ales specializarea CTI.",
            "IEC": "Ai o gândire analitică. Specializarea ta este IEC.",
            "IETTI": "Ești curios și inventiv. Specializarea ta: IETTI.",
            "AIA": "Ai simț estetic și logic. AIA te reprezintă.",
            "IE": "Orientare tehnică solidă. Specializarea ta: IE."
        }

    def start_test(self):
        name = self.name_input.text().strip()
        if not name:
            self.result_label.setText("Trebuie să introduci un nume!")
            return

        self.user_data["nume"] = name
        self.loading_wheel.show()
        self.start_button.setEnabled(False)
        self.result_label.setText("")
        self.explanation_label.setText("")
        self.avatar_label.clear()
        self.extra_button.hide()
        QTimer.singleShot(2000, self.process_result)

    def process_result(self):
        self.loading_wheel.hide()
        self.start_button.setEnabled(True)

        specializare = random.choice(list(self.specializari_text.keys()))
        self.user_data["specializare"] = specializare

        pixmap, avatar_path = AvatarGenerator.generate()
        self.user_data["avatar"] = avatar_path

        self.save_to_csv(self.user_data["nume"], specializare, avatar_path)

        if pixmap:
            self.avatar_label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))

        self.result_label.setText(f"{self.user_data['nume']}, specializarea ta este: {specializare}")
        self.explanation_label.setText(self.specializari_text[specializare])

        self.extra_button.setText(f"Joacă Jocul {specializare}")
        self.extra_button.show()

    def save_to_csv(self, name, spec, avatar_path):
        root_dir = os.path.dirname(os.path.dirname(current_dir))
        folder_games = os.path.join(root_dir, "../Games")
        if not os.path.exists(folder_games):
            os.makedirs(folder_games)
        full_path = os.path.join(folder_games, "database.csv")
        file_exists = os.path.isfile(full_path)

        try:
            with open(full_path, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Nume", "Avatar", "Specializare", "Punctaj"])
                writer.writerow([name, avatar_path, spec, 0])
        except Exception as e:
            print(f"[EROARE CSV] {e}")

    def start_joc_simplu(self):
        nume = self.user_data["nume"]
        avatar = self.user_data["avatar"]
        spec = self.user_data["specializare"]

        fisiere_joc = {
            "AIA": "AiaGame.py",
            "IE": "IEGame.py",
            "IEC": "joc_iec.py",
            "IETTI": "Joc-IETTI.py",
            "CTI": "ctiGame.py"
        }

        script = fisiere_joc.get(spec)
        if not script:
            print(f"Nu există joc pentru {spec}")
            return

        project_root = None
        path_check = current_dir
        while True:
            if os.path.exists(os.path.join(path_check, "../Games")):
                project_root = path_check
                break
            new_path = os.path.dirname(path_check)
            if new_path == path_check:
                break
            path_check = new_path

        if not project_root:
            print("EROARE: Nu am găsit folderul Games!")
            return

        cale_joc = os.path.join(project_root, ".", script)
        if os.path.exists(cale_joc):
            self.close_main_window.emit()
            os.system(f'python3 "{cale_joc}" "{nume}" "{avatar}" "{spec}"')
        else:
            print(f"EROARE: Nu găsesc fișierul {cale_joc}")
