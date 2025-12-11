import pygame
import sys
import time
import csv
import os
import random

# --- 1. CONFIGURARE JUCĂTOR (Argumente din Panel) ---
# Verificăm dacă primim argumentele din aplicație
if len(sys.argv) > 3:
    player_name = sys.argv[1]
    player_avatar = sys.argv[2]
    player_spec = sys.argv[3]
else:
    # Valori default pentru testare manuală
    player_name = "PlayerTest"
    # Cale relativă pentru avatar default
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    player_avatar = os.path.join(project_root, "asset", "avatar_downloaded.png")
    player_spec = "AIA"

# --- 2. CONFIGURARE PYGAME ---
pygame.init()
WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f"Logica ({player_spec}) - Jucator: {player_name}")

# Culori
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


# --- 3. FUNCȚIA DE SALVARE ÎN CSV ---
def save_score_csv(nume, avatar, specializare, punctaj):
    # Calculăm calea absolută către database.csv din folderul curent (Games)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_dir, "database.csv")
    file_exists = os.path.isfile(filename)

    try:
        with open(filename, mode='a', newline='', encoding='utf-8') as f:
            # Definim coloanele (inclusiv Specializare)
            fieldnames = ["Nume", "Avatar", "Specializare", "Punctaj"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            # Dacă fișierul nu există, scriem antetul
            if not file_exists:
                writer.writeheader()

            # Scriem datele jucătorului
            writer.writerow({
                "Nume": nume,
                "Avatar": avatar,
                "Specializare": specializare,
                "Punctaj": punctaj
            })
            print(f"[SUCCES] Scorul lui {nume} ({punctaj}) a fost salvat!")

    except Exception as e:
        print(f"[EROARE] Nu am putut salva in CSV: {e}")


# --- 4. CLASE JOC ---
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

    def get_type(self):
        return self.types[self.type_idx]

    def process(self, in1, in2):
        t = self.get_type()
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
        text = FONT.render(self.get_type(), True, WIRE_COLOR)
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
        lbl = FONT.render("OUT", True, WIRE_COLOR)
        surface.blit(lbl, (self.rect.x + 10, self.rect.y - 30))


# --- 5. INITIALIZARE OBIECTE ---
switches = [Switch(100, 150, "A"), Switch(100, 250, "B"), Switch(100, 350, "C"), Switch(100, 450, "D")]
gates = [Gate(350, 200), Gate(350, 400), Gate(600, 300)]
bulb = Bulb(800, 300)


# Funcție helper desenare fire
def draw_wire(start_rect, end_pos):
    mid_x = (start_rect.right + end_pos[0]) // 2
    pts = [start_rect.midright, (mid_x, start_rect.centery), (mid_x, end_pos[1]), end_pos]
    pygame.draw.lines(SCREEN, WIRE_COLOR, False, pts, 3)


# --- 6. GENERARE NIVEL VALID (Start Stins) ---
def calculate_circuit():
    r1 = gates[0].process(switches[0].state, switches[1].state)
    r2 = gates[1].process(switches[2].state, switches[3].state)
    return gates[2].process(r1, r2)


attempts = 0
while True:
    attempts += 1
    for g in gates: g.randomize_type()
    for s in switches: s.randomize()
    if calculate_circuit() == 0:
        bulb.state = 0
        break
print(f"Joc generat dupa {attempts} incercari.")

# --- 7. GAME LOOP ---
MAX_SCORE = 5000
start_time = time.time()
clicks = 0
game_over = False
final_score = 0
saved_to_db = False  # Flag ca să salvăm o singură dată

clock = pygame.time.Clock()
running = True

while running:
    SCREEN.fill(BLACK)
    current_time = time.time()

    # Logică circuit
    bulb.state = calculate_circuit()

    # Calcul scor
    if not game_over:
        elapsed = int(current_time - start_time)
        current_score = MAX_SCORE - (elapsed * 5) - (clicks * 50)
        if current_score < 0: current_score = 0

        # Verificare victorie
        if bulb.state == 1:
            game_over = True
            final_score = current_score

    # SALVARE AUTOMATĂ (Se execută o singură dată când câștigi)
    if game_over and not saved_to_db:
        save_score_csv(player_name, player_avatar, player_spec, final_score)
        saved_to_db = True

    # Evenimente
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
                # Dacă jocul e gata (Game Over), click oriunde închide jocul
                # Acest lucru permite întoarcerea la aplicația principală
                running = False

    # Desenare
    # Fire
    draw_wire(switches[0].rect, (gates[0].rect.x, gates[0].rect.y + 15))
    draw_wire(switches[1].rect, (gates[0].rect.x, gates[0].rect.y + 45))
    draw_wire(switches[2].rect, (gates[1].rect.x, gates[1].rect.y + 15))
    draw_wire(switches[3].rect, (gates[1].rect.x, gates[1].rect.y + 45))
    draw_wire(gates[0].rect, (gates[2].rect.x, gates[2].rect.y + 15))
    draw_wire(gates[1].rect, (gates[2].rect.x, gates[2].rect.y + 45))
    draw_wire(gates[2].rect, bulb.rect.center)

    # Componente
    for obj in switches + gates: obj.draw(SCREEN)
    bulb.draw(SCREEN)

    # HUD
    score_col = WHITE if current_score > 3000 else RED_OFF
    sc_txt = BIG_FONT.render(f"SCOR: {current_score}", True, score_col)
    SCREEN.blit(sc_txt, (WIDTH - 300, 20))

    stats = FONT.render(f"Spec: {player_spec} | Moves: {clicks}", True, GRAY)
    SCREEN.blit(stats, (20, 20))

    # Game Over Screen
    if game_over:
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(200)
        s.fill(BLACK)
        SCREEN.blit(s, (0, 0))

        t1 = BIG_FONT.render("CIRCUIT ACTIVAT!", True, GOLD)
        t2 = FONT.render(f"Bravo, {player_name}!", True, WHITE)
        t3 = FONT.render(f"Scor Final: {final_score}", True, GREEN_ON)
        t4 = FONT.render("Click oriunde pentru a continua...", True, GRAY)

        cx, cy = WIDTH // 2, HEIGHT // 2
        SCREEN.blit(t1, t1.get_rect(center=(cx, cy - 60)))
        SCREEN.blit(t2, t2.get_rect(center=(cx, cy)))
        SCREEN.blit(t3, t3.get_rect(center=(cx, cy + 50)))
        SCREEN.blit(t4, t4.get_rect(center=(cx, cy + 100)))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()