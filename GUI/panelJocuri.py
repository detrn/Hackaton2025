import sys
import random
import csv
import os
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPixmap

# Configurare cale pentru a importa AvatarGenerator din folderul părinte/curent
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from avatar_generator import AvatarGenerator
except ImportError:
    # Fallback dacă nu găsește fișierul (pentru testare)
    class AvatarGenerator:
        @staticmethod
        def generate():
            return None, "asset/avatar_downloaded.png"


# --- Clasa pentru animația de încărcare ---
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
        if self.angle >= 360: self.angle = 0
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


# --- PANELUL PRINCIPAL ---
class PanelJocuri(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Aici stocăm datele utilizatorului curent
        self.user_data = {
            'nume': '',
            'specializare': '',
            'avatar': ''
        }

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 1. Instrucțiuni
        label_instr = QLabel("Introdu numele și lasă programul să ghicească specializarea:")
        label_instr.setWordWrap(True)
        label_instr.setAlignment(Qt.AlignCenter)
        label_instr.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label_instr)

        # 2. Input Nume
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nume student")
        self.name_input.setFixedHeight(40)
        self.name_input.setFixedWidth(250)
        self.name_input.setStyleSheet("font-size: 14px; padding: 6px; border: 2px solid #4CAF50; border-radius: 8px;")
        layout.addWidget(self.name_input, alignment=Qt.AlignCenter)

        # 3. Buton Generare
        self.start_button = QPushButton("Generează Avatar & Profil")
        self.start_button.setFixedHeight(50)
        self.start_button.setFixedWidth(250)
        self.start_button.setStyleSheet("font-size: 14px; background-color: #4CAF50; color: white; border-radius: 8px;")
        self.start_button.clicked.connect(self.start_test)
        layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        # 4. Roata de încărcare
        self.loading_wheel = LoadingWheel()
        self.loading_wheel.setFixedSize(60, 60)
        self.loading_wheel.hide()
        layout.addWidget(self.loading_wheel, alignment=Qt.AlignCenter)

        # 5. Label Avatar
        self.avatar_label = QLabel()
        self.avatar_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.avatar_label, alignment=Qt.AlignCenter)

        # 6. Label Rezultat (Text)
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2E4053; padding: 10px;")
        layout.addWidget(self.result_label)

        self.explanation_label = QLabel("")
        self.explanation_label.setAlignment(Qt.AlignCenter)
        self.explanation_label.setWordWrap(True)
        self.explanation_label.setStyleSheet("font-size: 20px; color: #34495E;")
        layout.addWidget(self.explanation_label)

        # 7. Buton Start Joc (Ascuns inițial)
        self.extra_button = QPushButton("Start Joc (Punctaj)")
        self.extra_button.setMinimumHeight(60)
        self.extra_button.setStyleSheet("font-size: 14px; background-color: #FF5733; color: white; border-radius: 8px;")
        self.extra_button.hide()
        self.extra_button.clicked.connect(self.start_joc_simplu)
        layout.addWidget(self.extra_button, alignment=Qt.AlignCenter)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(layout)

        # Texte pentru specializări
        self.specializari_text = {
            "CTI": "Pari un tip pragmatic. De aceea am ales specializarea CTI.",
            "IEC": "Ai o gândire analitică și ești orientat spre inginerie. Am ales IEC.",
            "IETTI": "Ești curios și inventiv. Specializarea ta este IETTI.",
            "AIA": "Ai simț estetic și logic. AIA e perfect pentru tine.",
            "IE": "Ești orientat spre inginerie aplicată. Specializarea ta: IE."
        }

    def start_test(self):
        """Pornește simularea de 'gândire' a programului"""
        name = self.name_input.text().strip()
        if not name:
            self.result_label.setText("Trebuie să introduci un nume!")
            return

        # Salvăm numele temporar
        self.user_data['nume'] = name

        # UI Updates
        self.loading_wheel.show()
        self.result_label.setText("")
        self.explanation_label.setText("")
        self.avatar_label.clear()
        self.extra_button.hide()
        self.start_button.setEnabled(False)

        # Așteaptă 2 secunde apoi afișează rezultatul
        QTimer.singleShot(2000, self.process_result)

    def process_result(self):
        """Generează datele finale: Avatar și Specializare"""
        self.loading_wheel.hide()
        self.start_button.setEnabled(True)

        # 1. Alegem Specializare Random
        specializare = random.choice(list(self.specializari_text.keys()))
        mesaj = self.specializari_text[specializare]

        # 2. Generăm Avatar
        pixmap, avatar_path = AvatarGenerator.generate()

        # 3. Actualizăm datele utilizatorului în clasă
        self.user_data['specializare'] = specializare
        self.user_data['avatar'] = avatar_path

        # 4. Salvăm în CSV (Înregistrare inițială)
        self.save_to_csv(self.user_data['nume'], specializare, avatar_path)

        # 5. Afișare UI
        if pixmap:
            self.avatar_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.result_label.setText(f"{self.user_data['nume']}, specializarea ta este: {specializare}")
        self.explanation_label.setText(mesaj)

        # Arătăm butonul de joc
        self.extra_button.show()
        self.extra_button.setText(f"Joacă jocul {specializare}")

    def save_to_csv(self, name, spec, avatar_path):
        """Salvează utilizatorul în baza de date"""
        # Căutăm folderul Games relativ la GUI
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        folder_games = os.path.join(root_dir, "Games")

        if not os.path.exists(folder_games):
            os.makedirs(folder_games)

        full_path = os.path.join(folder_games, "database.csv")
        file_exists = os.path.isfile(full_path)

        try:
            with open(full_path, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Header dacă fișierul e nou
                if not file_exists:
                    writer.writerow(["Nume", "Avatar", "Specializare", "Punctaj"])

                # Scriem datele (Punctaj 0 inițial)
                writer.writerow([name, avatar_path, spec, 0])
                print(f"[DB] Salvat: {name} | {spec}")
        except Exception as e:
            print(f"[EROARE CSV] {e}")

    def start_joc_simplu(self):
        """Lansează jocul corespunzător specializării"""
        # 1. Luăm datele din self.user_data (populate în process_result)
        spec = self.user_data.get('specializare', 'AIA')
        nume = self.user_data.get('nume', 'Guest')
        avatar = self.user_data.get('avatar', '')

        # 2. Mapare Jocuri
        fisiere_joc = {
            "AIA": "AiaGame.py",
            "IE": "IEGame.py",
            "IEC": "joc_iec.py",
            "IETTI": "Joc-IETTI.py",
            "CTI": "AiaGame.py"
        }
        script_joc = fisiere_joc.get(spec)

        if not script_joc:
            print(f"Nu există joc pentru {spec}")
            return

        # 3. Construire Cale Joc
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        cale_joc = os.path.join(root_dir, 'Games', script_joc)

        # 4. Lansare
        if os.path.exists(cale_joc):
            print(f"Lansare {script_joc}...")
            self.close()  # Închidem GUI-ul
            # Trimitem 3 argumente: Nume, Avatar, Specializare
            subprocess.run([sys.executable, cale_joc, nume, avatar, spec])
        else:
            print(f"EROARE: Nu găsesc fișierul {cale_joc}")