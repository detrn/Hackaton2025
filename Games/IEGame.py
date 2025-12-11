import pygame
import random
import time
import sys
import os
import csv

# --- 1. CONFIGURARE (Argumente din Panel) ---
if len(sys.argv) > 3:
    PLAYER_NAME = sys.argv[1]
    PLAYER_AVATAR = sys.argv[2]
    PLAYER_SPEC = sys.argv[3]
else:
    PLAYER_NAME = "TestPlayer"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    PLAYER_AVATAR = os.path.join(project_root, "asset", "avatar_downloaded.png")
    PLAYER_SPEC = "IE"


# --- 2. SALVARE CSV (Ordinea cerută) ---
def save_score_csv(nume, avatar, specializare, punctaj):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_dir, "database.csv")
    file_exists = os.path.isfile(filename)

    try:
        with open(filename, mode='a', newline='', encoding='utf-8') as f:
            # Ordinea coloanelor: Specializare e penultima, Punctaj ultima
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
            print(f"[DB] Salvat: {nume} | {specializare} | {punctaj}")
    except Exception as e:
        print(f"[EROARE CSV] {e}")


class IEGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 500))
        pygame.display.set_caption(f"IE ({PLAYER_SPEC}) - Jucator: {PLAYER_NAME}")

        self.FONT = pygame.font.Font(None, 50)
        self.SMALL_FONT = pygame.font.Font(None, 30)

        self.STATE_MENU = 0
        self.STATE_GAME = 1
        self.STATE_COMPLETE = 2
        self.state = self.STATE_MENU
        self.score_saved = False

        self.WIRE_COLORS = [(255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 0), (0, 255, 255),
                            (255, 165, 0)]
        self.LEFT_X = 150
        self.Y_POSITIONS = [100, 160, 220, 280, 340, 400, 460]
        self.TARGET_AREAS = [{"color": color, "rect": pygame.Rect(600, y - 30, 100, 60)} for color, y in
                             zip(self.WIRE_COLORS, self.Y_POSITIONS)]

        self.wires = []
        self.dragging = None
        self.TIMER_START = 30
        self.MAX_SCORE = 5000  # Limita maximă scor
        self.reset_wires()

    def reset_wires(self):
        random.shuffle(self.Y_POSITIONS)
        self.wires = [{"color": c, "start": [self.LEFT_X, y], "placed": False} for c, y in
                      zip(self.WIRE_COLORS, self.Y_POSITIONS)]
        self.dragging = None
        self.round_start_time = time.time()
        self.round_score = 0
        self.time_left = self.TIMER_START
        self.score_saved = False
        self.last_tick = time.time()

    def draw_button(self, text, x, y, w, h):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        color = (120, 120, 120) if (x < mouse[0] < x + w and y < mouse[1] < y + h) else (70, 70, 70)
        pygame.draw.rect(self.screen, color, (x, y, w, h), border_radius=12)
        label = self.FONT.render(text, True, (255, 255, 255))
        self.screen.blit(label, label.get_rect(center=(x + w // 2, y + h // 2)))
        return click[0] == 1 and x < mouse[0] < x + w and y < mouse[1] < y + h

    def draw_game(self):
        self.screen.fill((30, 30, 30))
        now = time.time()
        if now - self.last_tick >= 1:
            self.time_left -= 1
            self.last_tick = now

        if self.time_left <= 0: self.state = self.STATE_COMPLETE

        self.screen.blit(self.FONT.render(f"Timp: {int(self.time_left)}", True, (255, 255, 255)), (20, 20))
        self.screen.blit(self.FONT.render(f"Scor: {self.round_score}", True, (255, 255, 255)), (600, 20))

        for area in self.TARGET_AREAS:
            pygame.draw.rect(self.screen, area["color"], area["rect"])
            self.screen.blit(self.SMALL_FONT.render("Circuit", True, (255, 255, 255)),
                             (area["rect"].x + 10, area["rect"].y + 10))

        for w in self.wires:
            pygame.draw.circle(self.screen, w["color"], w["start"], 20)
            if self.dragging == w:
                mx, my = pygame.mouse.get_pos()
                pygame.draw.line(self.screen, w["color"], w["start"], (mx, my), 5)
                pygame.draw.circle(self.screen, w["color"], (mx, my), 15)

        if all(w["placed"] for w in self.wires):
            time_used = time.time() - self.round_start_time
            # Calcul scor: 5000 - penalizare timp. Nu mai mult de 5000.
            score = int(self.MAX_SCORE - (time_used * 100))
            self.round_score = max(0, min(score, self.MAX_SCORE))
            self.state = self.STATE_COMPLETE

    def draw_complete(self):
        self.screen.fill((20, 20, 20))
        self.screen.blit(self.FONT.render("Circuit Complet!", True, (0, 255, 0)), (250, 180))
        self.screen.blit(self.SMALL_FONT.render(f"Scor final: {self.round_score}", True, (255, 255, 255)), (300, 260))

        if not self.score_saved:
            save_score_csv(PLAYER_NAME, PLAYER_AVATAR, PLAYER_SPEC, self.round_score)
            self.score_saved = True

        if self.draw_button("Iesire (Leaderboard)", 250, 350, 350, 60):
            pygame.quit()
            sys.exit()  # Ieșire curată pentru a reveni la GUI

    def draw_menu(self):
        self.screen.fill((25, 25, 25))
        self.screen.blit(self.FONT.render("IE - Electricitate", True, (255, 255, 255)), (250, 120))
        if self.draw_button("Start Joc", 300, 250, 200, 60):
            self.state = self.STATE_GAME
            self.reset_wires()

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for w in self.wires:
                if not w["placed"]:
                    sx, sy = w["start"]
                    if abs(mx - sx) < 20 and abs(my - sy) < 20: self.dragging = w
        if event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                mx, my = pygame.mouse.get_pos()
                for area in self.TARGET_AREAS:
                    if area["rect"].collidepoint(mx, my) and area["color"] == self.dragging["color"]:
                        self.dragging["start"] = [area["rect"].centerx, area["rect"].centery]
                        self.dragging["placed"] = True
                self.dragging = None

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if self.state == self.STATE_GAME: self.handle_events(event)

            if self.state == self.STATE_MENU:
                self.draw_menu()
            elif self.state == self.STATE_GAME:
                self.draw_game()
            elif self.state == self.STATE_COMPLETE:
                self.draw_complete()

            pygame.display.update()
        pygame.quit()


if __name__ == "__main__":
    IEGame().run()