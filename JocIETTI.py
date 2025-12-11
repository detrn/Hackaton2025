import subprocess
import sys
import math
import random
import os
import csv
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QGraphicsOpacityEffect, QHBoxLayout
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPolygonF
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer, QPointF, QRectF

# --- 1. CONFIGURARE ---
if len(sys.argv) > 3:
    PLAYER_NAME = sys.argv[1]
    PLAYER_AVATAR = sys.argv[2]
    PLAYER_SPEC = sys.argv[3]
else:
    PLAYER_NAME = "TestPlayer"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    PLAYER_AVATAR = os.path.join(project_root, "asset", "avatar_downloaded.png")
    PLAYER_SPEC = "IETTI"

# --- CULORI NEON ---
BG_COLOR = QColor(10, 15, 30)
GRID_COLOR = QColor(30, 40, 60)
NEON_GREEN = QColor(50, 255, 50)
NEON_RED = QColor(255, 50, 80)
NEON_BLUE = QColor(0, 200, 255)
NEON_YELLOW = QColor(255, 230, 0)
WHITE = QColor(255, 255, 255)


# --- 2. SALVARE CSV ---
def save_score_csv(nume, avatar, specializare, punctaj):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_dir, "../Games/database.csv")
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


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)  # Viteza mai mica pt performanta
        self.vy = random.uniform(-3, 3)
        self.radius = random.randint(2, 4)
        self.color = QColor(color)
        self.life = 200  # Viata mai scurta


class SignalGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"IETTI: Signal Master - {PLAYER_NAME}")

        # Ascunde cursorul pentru Touchscreen
        self.setCursor(Qt.CursorShape.BlankCursor)

        self.offset_x = 0

        # Variabile joc
        self.MAX_SCORE = 5000
        self.time_limit = 20
        self.score_pachete_salvate = 0
        self.final_score = 0
        self.score_saved = False
        self.game_active = True

        # Parametri undă
        self.phase = 0
        self.player_amp = 50
        self.target_amp = 100
        self.freq = 0.04

        self.particles = []

        # Timer (Game Loop) - Setat la 30 FPS pentru performanta pe Raspberry Pi
        # 1000ms / 30fps = ~33ms
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.update_game)
        self.anim_timer.start(33)
        self.game_start_timestamp = None

        # --- UI SETUP ---
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Header
        self.header = QWidget()
        self.header.setStyleSheet("background-color: black; border-bottom: 2px solid #00C8FF;")
        self.header.setFixedHeight(60)

        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        text_layout = QHBoxLayout()
        font_hud = QFont("Consolas", 16, QFont.Weight.Bold)

        self.score_label = QLabel(f"PACHETE: {self.score_pachete_salvate}")
        self.score_label.setFont(font_hud)
        self.score_label.setStyleSheet(f"color: {NEON_YELLOW.name()}; border: none;")

        self.time_label = QLabel("60.0s")
        self.time_label.setFont(font_hud)
        self.time_label.setStyleSheet(f"color: white; border: none;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        text_layout.addWidget(self.score_label)
        text_layout.addStretch()
        text_layout.addWidget(self.time_label)
        header_layout.addLayout(text_layout)

        self.layout.addWidget(self.header, alignment=Qt.AlignmentFlag.AlignTop)
        self.layout.addStretch()

        # Instructions
        self.instr_label = QLabel("TAP UP / DOWN to Calibrate")
        self.instr_label.setFont(QFont("Consolas", 14))
        self.instr_label.setStyleSheet("color: rgba(100, 200, 255, 150); background: transparent; margin-bottom: 20px;")
        self.instr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.instr_label)

        # Game Over Screen
        self.game_over_widget = QWidget()
        self.game_over_widget.setStyleSheet("background-color: rgba(0, 0, 0, 220);")
        go_layout = QVBoxLayout(self.game_over_widget)
        go_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.go_title = QLabel("MISSION COMPLETE")
        self.go_title.setFont(QFont("Consolas", 48, QFont.Weight.Bold))
        self.go_title.setStyleSheet(f"color: {NEON_GREEN.name()};")
        self.go_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.go_score = QLabel("")
        self.go_score.setFont(QFont("Consolas", 28, QFont.Weight.Bold))
        self.go_score.setStyleSheet(f"color: {NEON_YELLOW.name()};")
        self.go_score.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.leaderboard_btn = QPushButton(">> CLICK PENTRU CLASAMENT <<")
        self.leaderboard_btn.setFont(QFont("Consolas", 18))
        self.leaderboard_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.leaderboard_btn.setStyleSheet(
            f"background-color: transparent; color: white; border: 2px solid {NEON_BLUE.name()}; padding: 10px 20px;")
        self.leaderboard_btn.clicked.connect(self.go_to_leaderboard)

        go_layout.addWidget(self.go_title)
        go_layout.addWidget(self.go_score)
        go_layout.addWidget(self.leaderboard_btn)

        self.game_over_widget.setParent(self)
        self.game_over_widget.hide()

        self.new_target()

    def resizeEvent(self, event):
        self.game_over_widget.resize(self.size())
        super().resizeEvent(event)

    def new_target(self):
        self.target_amp = random.randint(40, 200)

    def mousePressEvent(self, event):
        if self.game_active:
            # Control tactil simplificat
            if event.pos().y() < self.height() // 2:
                if self.player_amp < 300: self.player_amp += 10
            else:
                if self.player_amp > 10: self.player_amp -= 10

    def create_explosion(self, x, y, color):
        # Reducem numarul de particule pentru performanta
        for _ in range(8):
            self.particles.append(Particle(x, y, color))

    def update_game(self):
        # Update Grid mai rar
        self.offset_x += 2
        if self.offset_x > 60: self.offset_x = 0

        if self.game_active:
            if self.game_start_timestamp is None:
                self.game_start_timestamp = 0  # Simplificat

            # Folosim un counter intern simplu pentru timp
            # Fiecare tick e 33ms
            self.game_start_timestamp += 33
            elapsed = self.game_start_timestamp / 1000.0
            time_left = max(0, self.time_limit - elapsed)

            current_score = int(self.MAX_SCORE - (elapsed * 50) + (self.score_pachete_salvate * 100))
            current_score = max(0, current_score)

            self.time_label.setText(f"{time_left:.1f}s")

            if time_left < 10:
                self.time_label.setStyleSheet(f"color: {NEON_RED.name()}; font-weight: bold;")

            diff = abs(self.player_amp - self.target_amp)
            if diff < 15:  # Marja mai permisiva
                self.score_pachete_salvate += 1
                self.score_label.setText(f"PACHETE: {self.score_pachete_salvate}")
                self.create_explosion(self.width() // 2, self.height() // 2, NEON_YELLOW)
                self.new_target()

            if time_left <= 0:
                self.game_active = False
                self.final_score = current_score
                self.show_game_over()

        # Update particles
        for p in self.particles[:]:
            p.x += p.vx
            p.y += p.vy
            p.life -= 15  # Dispar mai repede
            if p.life <= 0:
                self.particles.remove(p)

        self.phase += 0.3
        self.update()  # Redeseneaza ecranul

    def show_game_over(self):
        if not self.score_saved:
            save_score_csv(PLAYER_NAME, PLAYER_AVATAR, PLAYER_SPEC, self.final_score)
            self.score_saved = True

        self.header.setVisible(False)
        self.instr_label.setVisible(False)
        self.go_score.setText(f"SCOR FINAL: {self.final_score}")
        self.game_over_widget.setVisible(True)
        self.game_over_widget.raise_()

        # Fara animatie fade-in complexa pentru performanta
        opacity_effect = QGraphicsOpacityEffect()
        self.game_over_widget.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(1)

    def go_to_leaderboard(self):
        self.close()
        try:
            subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "leaderboard.py")])
        except Exception as e:
            print(f"Eroare: {e}")

    def draw_glow_polyline(self, painter, points, color, width=2):
        """ Varianta Optimizata: Doar 2 straturi in loc de 3 """
        if not points: return

        # 1. Glow (Transparent si lat)
        glow_color = QColor(color)
        glow_color.setAlpha(60)  # Mai putin transparent pentru vizibilitate
        painter.setPen(
            QPen(glow_color, width + 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.drawPolyline(points)

        # 2. Core (Solid)
        color.setAlpha(255)
        painter.setPen(QPen(color, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.drawPolyline(points)

    def paintEvent(self, event):
        painter = QPainter(self)
        # Antialiasing-ul consuma mult. Il oprim pentru performanta maxima daca inca e lag.
        # Daca e ok, poti decomenta linia urmatoare:
        # painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # --- FUNDAL ---
        painter.fillRect(self.rect(), BG_COLOR)

        # --- GRID OPTIMIZAT ---
        pen = QPen(GRID_COLOR)
        pen.setWidth(1)
        painter.setPen(pen)

        w, h = self.width(), self.height()
        spacing = 60  # Grid mai larg = mai putine linii de desenat

        # Linii verticale
        for x in range(0, w, spacing):
            draw_x = int((x + self.offset_x) % w)
            painter.drawLine(draw_x, 0, draw_x, h)

        # Linii orizontale
        for y in range(0, h, spacing):
            painter.drawLine(0, y, w, y)

        # Linie centrala
        center_pen = QPen(QColor(50, 60, 80))
        center_pen.setWidth(2)
        painter.setPen(center_pen)
        painter.drawLine(0, h // 2, w, h // 2)

        # --- UNDE ---
        offset_y = h // 2

        # OPTIMIZARE CRITICA: Calculam puncte din 10 in 10 pixeli (step=10)
        # Inainte era 5. Asta reduce calculul la jumatate.
        step = 10

        # Target Wave
        points_target = []
        for x in range(0, w + step, step):
            y = offset_y + math.sin((x * self.freq) + self.phase) * self.target_amp
            points_target.append(QPointF(float(x), y))

        # Player Wave
        points_player = []
        for x in range(0, w + step, step):
            y = offset_y + math.sin((x * self.freq) + self.phase) * self.player_amp
            points_player.append(QPointF(float(x), y))

        self.draw_glow_polyline(painter, points_target, NEON_RED, 3)
        self.draw_glow_polyline(painter, points_player, NEON_GREEN, 4)

        # --- UI ELEMENTS ---
        if self.game_active:
            diff = abs(self.player_amp - self.target_amp)
            bar_color = NEON_RED if diff > 15 else NEON_GREEN

            # Bara simplificata (fara glow separat)
            painter.setBrush(QBrush(bar_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(int(w - 30), int(offset_y - diff), 15, int(diff * 2))

        # Particule
        for p in self.particles:
            c = QColor(p.color)
            c.setAlpha(180)  # Transparenta fixa pentru viteza
            painter.setBrush(QBrush(c))
            painter.drawEllipse(QPointF(p.x, p.y), p.radius, p.radius)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignalGame()
    window.showFullScreen()  # FullScreen pentru Raspberry Pi
    sys.exit(app.exec())