import pygame
import sys
import time
import csv
import os
import random
import subprocess

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
    PLAYER_SPEC = "AIA"


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


# --- 3. CONFIGURARE PYGAME ---
pygame.init()
WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f"AIA Logic - Jucător: {PLAYER_NAME}")

# CULORI
BLACK = (20, 20, 25)
WHITE = (230, 230, 230)
GREEN_ON = (50, 255, 50)
RED_OFF = (200, 50, 50)
DARK_BLUE = (40, 60, 100)
WIRE_COLOR = (150, 150, 150)
GOLD = (255, 215, 0)
GRAY = (100, 100, 100)

FONT = pygame.font.SysFont('consolas', 24, bold=True)
BIG_FONT = pygame.font.SysFont('consolas', 40, bold=True)


# --- CLASE ---
class Switch:
    def __init__(self, x, y, label):
        self.rect = pygame.Rect(x, y, 60, 60)
        self.state = 0
        self.label = label

    def randomize(self):
        self.state = random.choice([0, 1])

    def draw(self, surface):
        color = GREEN_ON if self.state else RED_OFF
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)
        val_text = FONT.render(str(self.state), True, BLACK if self.state else WHITE)
        surface.blit(val_text, val_text.get_rect(center=self.rect.center))
        lbl_text = FONT.render(self.label, True, GRAY)
        surface.blit(lbl_text, (self.rect.x, self.rect.y - 25))

    def toggle(self):
        self.state = 1 - self.state


class Gate:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 100, 60)
        self.types = ["AND", "OR", "XOR", "NAND"]
        self.type_idx = 0

    def randomize_type(self):
        self.type_idx = random.randint(0, len(self.types) - 1)

    def process(self, in1, in2):
        t = self.types[self.type_idx]
        if t == "AND":
            return in1 & in2
        elif t == "OR":
            return in1 | in2
        elif t == "XOR":
            return in1 ^ in2
        elif t == "NAND":
            return 0 if (in1 & in2) else 1
        return 0

    def draw(self, surface):
        pygame.draw.rect(surface, DARK_BLUE, self.rect, border_radius=5)
        pygame.draw.rect(surface, WIRE_COLOR, self.rect, 2, border_radius=5)
        text = FONT.render(self.types[self.type_idx], True, WIRE_COLOR)
        surface.blit(text, text.get_rect(center=self.rect.center))


class Bulb:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 60)
        self.state = 0

    def draw(self, surface):
        if self.state:
            pygame.draw.circle(surface, (50, 255, 50, 120), self.rect.center, 45)
        color = GREEN_ON if self.state else (40, 0, 0)
        pygame.draw.circle(surface, color, self.rect.center, 25)
        pygame.draw.circle(surface, WHITE, self.rect.center, 25, 3)


# --- SETUP ---
switches = [Switch(100, 150, "A"), Switch(100, 250, "B"), Switch(100, 350, "C"), Switch(100, 450, "D")]
gates = [Gate(350, 200), Gate(350, 400), Gate(600, 300)]
bulb = Bulb(800, 300)


def draw_wire(start_rect, end_pos):
    mid_x = (start_rect.right + end_pos[0]) // 2
    pts = [start_rect.midright, (mid_x, start_rect.centery), (mid_x, end_pos[1]), end_pos]
    pygame.draw.lines(SCREEN, WIRE_COLOR, False, pts, 3)


def calculate_circuit():
    r1 = gates[0].process(switches[0].state, switches[1].state)
    r2 = gates[1].process(switches[2].state, switches[3].state)
    return gates[2].process(r1, r2)


# Generare nivel valid
while True:
    for g in gates: g.randomize_type()
    for s in switches: s.randomize()
    if calculate_circuit() == 0:
        bulb.state = 0
        break

# --- MAIN LOOP ---
MAX_SCORE = 5000
start_time = time.time()
game_over = False
score_saved = False
next_action = None
clicks = 0
current_score = 5000  # Inițializare scor
time_left = 60  # Inițializare timp

running = True
while running:
    SCREEN.fill(BLACK)

    # --- LOGICA DE JOC (Se oprește dacă e Game Over) ---
    if not game_over:
        elapsed = time.time() - start_time
        time_left = max(0, 60 - elapsed)

        # Calcul scor dinamic
        current_score = int(MAX_SCORE - (elapsed * 50) - (clicks * 50))
        if current_score < 0: current_score = 0

        # Verificare circuit
        bulb.state = calculate_circuit()

        # Conditii STOP JOC
        if bulb.state == 1:
            game_over = True  # Victorie -> Scorul îngheață aici
        if time_left <= 0:
            game_over = True  # Timp expirat

    # --- EVENIMENTE ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not game_over:
                for sw in switches:
                    if sw.rect.collidepoint(event.pos):
                        sw.toggle()
                        clicks += 1
            else:
                # Daca jocul e gata, click oriunde duce la MainFrame
                next_action = "mainframe"
                running = False

    # --- DESENARE ---
    draw_wire(switches[0].rect, (gates[0].rect.x, gates[0].rect.y + 15))
    draw_wire(switches[1].rect, (gates[0].rect.x, gates[0].rect.y + 45))
    draw_wire(switches[2].rect, (gates[1].rect.x, gates[1].rect.y + 15))
    draw_wire(switches[3].rect, (gates[1].rect.x, gates[1].rect.y + 45))
    draw_wire(gates[0].rect, (gates[2].rect.x, gates[2].rect.y + 15))
    draw_wire(gates[1].rect, (gates[2].rect.x, gates[2].rect.y + 45))
    draw_wire(gates[2].rect, bulb.rect.center)

    for obj in switches + gates: obj.draw(SCREEN)
    bulb.draw(SCREEN)

    # UI (Afișează scorul înghețat dacă game_over e True)
    SCREEN.blit(BIG_FONT.render(f"SCOR: {current_score}", True, WHITE), (WIDTH - 300, 20))

    col_time = WHITE if time_left > 10 else RED_OFF
    SCREEN.blit(FONT.render(f"TIMP: {int(time_left)}s", True, col_time), (20, 20))

    if game_over:
        if not score_saved:
            save_score_csv(PLAYER_NAME, PLAYER_AVATAR, PLAYER_SPEC, current_score)
            score_saved = True

        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(200);
        s.fill(BLACK)
        SCREEN.blit(s, (0, 0))

        txt = "CIRCUIT REUSIT!" if bulb.state == 1 else "TIMP EXPIRAT!"
        col = GOLD if bulb.state == 1 else RED_OFF

        t1 = BIG_FONT.render(txt, True, col)
        t2 = FONT.render(f"Scor Final: {current_score}", True, WHITE)
        t3 = FONT.render("Click oriunde pentru Clasament", True, GRAY)

        SCREEN.blit(t1, t1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
        SCREEN.blit(t2, t2.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        SCREEN.blit(t3, t3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

    pygame.display.flip()
    pygame.time.Clock().tick(30)

# --- FINALIZARE ---
pygame.quit()
if next_action == "mainframe":
    try:
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "MainFrame.py")])
    except Exception as e:
        print(f"Eroare lansare MainFrame: {e}")
sys.exit()