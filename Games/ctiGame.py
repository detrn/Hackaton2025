import subprocess
import sys
import random
import os
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
)
from PyQt5.QtWidgets import QGraphicsOpacityEffect

from PyQt5.QtGui import QFont, QColor, QPainter, QPen
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer

# --- 1. CONFIGURARE (FĂRĂ ID) ---
if len(sys.argv) > 3:
    PLAYER_NAME = sys.argv[1]
    PLAYER_AVATAR = sys.argv[2]
    PLAYER_SPEC = sys.argv[3]
else:
    PLAYER_NAME = "TestPlayer"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    PLAYER_AVATAR = os.path.join(project_root, "asset", "avatar_downloaded.png")
    PLAYER_SPEC = "CTI"


# --- 2. SALVARE CSV ---
def save_score_csv(nume, avatar, specializare, punctaj):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_dir, "database.csv")
    try:
        file_exists = os.path.isfile(filename)
        with open(filename, mode='a', newline='', encoding='utf-8') as f:
            fieldnames = ["Nume", "Avatar", "Specializare", "Punctaj"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "Nume": nume,
                "Avatar": avatar,
                "Specializare": specializare,
                "Punctaj": punctaj
            })
    except Exception as e:
        print(f"Eroare CSV: {e}")











QUESTIONS = [
    {
        "question": "for i in range(n): print(i)\nComplexitatea este:",
        "answer": "O(n)",
        "choices": ["O(1)", "O(log n)", "O(n)", "O(n^2)"]
    },
    {
        "question": "for i in range(n):\n    for j in range(n): print(i,j)\nComplexitatea este:",
        "answer": "O(n^2)",
        "choices": ["O(n)", "O(n log n)", "O(1)", "O(n^2)"]
    },
    {
        "question": "i = 1\nwhile i < n:\n    i *= 2\nComplexitatea este:",
        "answer": "O(log n)",
        "choices": ["O(n)", "O(n^2)", "O(log n)", "O(1)"]
    },
    {
        "question": "print('Hello')\nComplexitatea este:",
        "answer": "O(1)",
        "choices": ["O(1)", "O(n)", "O(log n)", "O(n^2)"]
    },
    {
        "question": "for i in range(n):\n    for j in range(100): print(i,j)\nComplexitatea este:",
        "answer": "O(n)",
        "choices": ["O(n)", "O(1)", "O(n^2)", "O(log n)"]
    }
]


from PyQt5.QtCore import QTimer, QPropertyAnimation, QEasingCurve

class BackgroundGrid(QWidget):
    """Desenează grid-ul animat pe fundal."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.offset_x = 0
        self.offset_y = 0

        # Timer pentru mișcarea grid-ului
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.update_offset)
        self.move_timer.start(50)  # actualizare la fiecare 50 ms

    def update_offset(self):
        # mișcare lentă pe diagonala
        self.offset_x += 0.5
        self.offset_y += 0.3

        # reset la fiecare 30 px pentru a nu crește indefinit
        if self.offset_x > 30:
            self.offset_x = 0
        if self.offset_y > 30:
            self.offset_y = 0

        self.update()  # redesenează grid-ul

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(25, 25, 25))

        pen = QPen(QColor(40, 40, 40))
        painter.setPen(pen)

        spacing = 30
        w, h = self.width(), self.height()

        for x in range(0, w, spacing):
            painter.drawLine(int(x + self.offset_x), 0, int(x + self.offset_x), h)
        for y in range(0, h, spacing):
            painter.drawLine(0, int(y + self.offset_y), w, int(y + self.offset_y))


class QuizWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CS Complexity Quiz")
        self.leaderboard_btn = QPushButton("Mergi la Leaderboard")
        # Fundal
        self.bg = BackgroundGrid()
        self.bg.setParent(self)

        # Game state
        self.score = 5000  # scor global
        self.min_score = 2000
        self.index = 0
        self.questions = random.sample(QUESTIONS, 5)

        # Timer global
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_score)
        self.timer_interval = 100  # 0.1 secunde
        self.total_game_time = 30 * 1000  # 30 secunde
        self.elapsed = 0
        self.score_decrement_per_tick = (5000 - self.min_score) * self.timer_interval / self.total_game_time

        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(50, 50, 50, 50)

        # Titlu
        self.title = QLabel("Ghicește Complexitatea (Big-O)")
        self.title.setFont(QFont("Arial", 26, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("color: white; margin-bottom: 20px;")
        self.layout.addWidget(self.title)

        # Întrebare
        self.q_label = QLabel("")
        self.q_label.setFont(QFont("Consolas", 18))
        self.q_label.setAlignment(Qt.AlignCenter)
        self.q_label.setWordWrap(True)
        self.q_label.setStyleSheet("color: #DDDDDD; margin-bottom: 25px;")
        self.layout.addWidget(self.q_label)

        # Layout pentru butoane
        self.buttons_layout = QVBoxLayout()
        self.layout.addLayout(self.buttons_layout)

        self.choice_buttons = []
        for _ in range(4):
            btn = QPushButton("")
            btn.setFont(QFont("Arial", 18))
            btn.clicked.connect(self.check_answer)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #333;
                    border: 2px solid #444;
                    padding: 14px;
                    border-radius: 10px;
                    color: white;
                }
                QPushButton:hover { background-color: #444; }
                QPushButton:pressed { background-color: #555; }
            """)
            self.choice_buttons.append(btn)
            self.buttons_layout.addWidget(btn)

        # Container pentru feedback ✔ ✘
        self.feedback_container = QLabel(self)
        self.feedback_container.setAlignment(Qt.AlignCenter)
        self.feedback_container.setStyleSheet("background: transparent;")
        self.feedback_container.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.feedback_container.setGeometry(self.rect())

        # Feedback label ✔ ✘
        self.feedback_label = QLabel("", self.feedback_container)
        self.feedback_label.setFont(QFont("Arial", 160, QFont.Bold))
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setStyleSheet("color: white; background: transparent;")
        self.feedback_label.setVisible(False)
        self.feedback_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Label pentru scor
        self.score_label = QLabel(f"Score: {self.score}", self)
        self.score_label.setFont(QFont("Arial", 22, QFont.Bold))
        self.score_label.setStyleSheet("color: #FFD700;")
        self.score_label.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.score_label)

        self.load_question()
        self.timer.start(self.timer_interval)  # pornește timer global

    def resizeEvent(self, event):
        self.bg.resize(self.size())
        self.feedback_container.setGeometry(self.rect())

    def load_question(self):
        if self.index >= len(self.questions):
            self.show_final_screen()
            return

        q = self.questions[self.index]
        self.q_label.setText(q["question"])

        choices = q["choices"][:]
        random.shuffle(choices)

        for btn, text in zip(self.choice_buttons, choices):
            btn.setText(text)
            btn.show()

    def update_score(self):
        # Scade puncte constant
        self.score = max(self.min_score, self.score - self.score_decrement_per_tick)
        self.score_label.setText(f"Score: {int(self.score)}")

        self.elapsed += self.timer_interval
        if self.elapsed >= self.total_game_time:
            self.elapsed = self.total_game_time
            # scorul nu mai scade după timpul maxim, dar timer-ul poate continua până la final
            self.score = max(self.min_score, self.score)
            self.score_label.setText(f"Score: {int(self.score)}")

    def animate_feedback(self, symbol, color):
        self.feedback_label.setText(symbol)
        self.feedback_label.setStyleSheet(f"color: {color}; background: transparent;")
        self.feedback_label.adjustSize()
        self.feedback_label.move(
            (self.width() - self.feedback_label.width()) // 2,
            (self.height() - self.feedback_label.height()) // 2
        )
        self.feedback_label.setWindowOpacity(0)
        self.feedback_label.setVisible(True)

        anim = QPropertyAnimation(self.feedback_label, b"windowOpacity")
        anim.setDuration(350)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.start()

        QTimer.singleShot(1200, lambda: self.feedback_label.setVisible(False))

    def check_answer(self):
        picked = self.sender().text()
        correct = self.questions[self.index]["answer"]

        if picked != correct:
            # răspuns greșit: scade 300 puncte
            self.score = max(self.min_score, self.score - 300)
            self.score_label.setText(f"Score: {int(self.score)}")
            self.animate_feedback("✘", "#FF5555")
        else:
            self.animate_feedback("✔", "#00FF7F")

        self.index += 1
        QTimer.singleShot(500, self.load_question)

    from PyQt5.QtGui import QFontDatabase

    from PyQt5.QtWidgets import QGraphicsOpacityEffect

    def show_final_screen(self):
        self.timer.stop()

        # Ascundem elementele vechi
        self.title.hide()
        self.q_label.hide()
        self.score_label.hide()
        for btn in self.choice_buttons:
            btn.hide()

        # ---- ECRAN FINAL ----
        # Titlu BigO Game
        title_label = QLabel("BigO Game")
        print(self.score)
        title_label.setFont(QFont("Arial", 60, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #00FFFF; margin-bottom: 20px;")
        self.layout.addWidget(title_label)

        # Efect de opacity pentru fade-in
        opacity_effect = QGraphicsOpacityEffect()
        title_label.setGraphicsEffect(opacity_effect)

        self.fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
        self.fade_anim.setDuration(800)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.start()

        # Bounce ușor pe verticală (simulat prin margin)
        def bounce():
            start_margin = 0
            end_margin = 20
            step = 4
            current = start_margin

            def animate_step():
                nonlocal current, step
                current += step
                if current > end_margin or current < start_margin:
                    step = -step
                    current += step
                title_label.setStyleSheet(f"color: #00FFFF; margin-bottom: {current}px;")
                if current != start_margin:
                    QTimer.singleShot(30, animate_step)

            animate_step()

        bounce()

        # Mesajul final cu scor
        finish_label = QLabel(f"Felicitări! Acesta este punctajul tău:\n{int(self.score)}")
        save_score_csv("Ionut",PLAYER_AVATAR,PLAYER_SPEC,int(self.score))
        finish_label.setFont(QFont("Arial", 34, QFont.Bold))
        finish_label.setAlignment(Qt.AlignCenter)
        finish_label.setStyleSheet("color: white; margin-bottom: 40px;")
        self.layout.addWidget(finish_label)

        # Buton leaderboard

        self.leaderboard_btn.setFont(QFont("Arial", 22))
        self.leaderboard_btn.setStyleSheet("""
            QPushButton {
                background-color: #2D7D9A;
                padding: 18px;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover { background-color: #389ABF; }
        """)
        self.layout.addWidget(self.leaderboard_btn)

        self.update()
        self.repaint()

        self.leaderboard_btn.clicked.connect(self.leaderboard_button_clicked)
    def leaderboard_button_clicked(self):
        QuizWindow.close(self)
        try:
            subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "leaderboard.py")])
        except Exception as e:
            print(f"Eroare lansare MainFrame: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuizWindow()
    window.showMaximized()
    sys.exit(app.exec_())
