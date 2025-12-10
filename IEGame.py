import pygame
import random
import time


class IEGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 500))
        pygame.display.set_caption("IE - Inginerie Electrică")

        # Fonts
        self.FONT = pygame.font.Font(None, 50)
        self.SMALL_FONT = pygame.font.Font(None, 30)

        # Stări
        self.STATE_MENU = 0
        self.STATE_GAME = 1
        self.STATE_COMPLETE = 2
        self.state = self.STATE_MENU

        # Fire (7 culori)
        self.WIRE_COLORS = [
            (255, 0, 0),       # roșu
            (0, 0, 255),       # albastru
            (255, 255, 0),     # galben
            (255, 0, 255),     # magenta
            (0, 255, 0),       # verde
            (0, 255, 255),     # cyan
            (255, 165, 0)      # portocaliu
        ]

        self.LEFT_X = 150
        self.Y_POSITIONS = [100, 160, 220, 280, 340, 400, 460]

        # Zone țintă
        self.TARGET_AREAS = [
            {"color": color, "rect": pygame.Rect(600, y - 30, 100, 60)}
            for color, y in zip(self.WIRE_COLORS, self.Y_POSITIONS)
        ]

        # Firele active
        self.wires = []
        self.dragging = None

        # Timer
        self.TIMER_START = 30   # 30 secunde per rundă
        self.time_left = self.TIMER_START
        self.last_tick = time.time()

        # Scor curent runda
        self.round_score = 0
        self.round_start_time = None

        self.reset_wires()

    # ===============================================
    # Funcții
    # ===============================================

    def reset_wires(self):
        random.shuffle(self.Y_POSITIONS)
        self.wires = []
        for color, y in zip(self.WIRE_COLORS, self.Y_POSITIONS):
            self.wires.append({
                "color": color,
                "start": [self.LEFT_X, y],
                "placed": False
            })
        self.dragging = None
        self.round_start_time = time.time()
        self.round_score = 0
        self.time_left = self.TIMER_START

    def draw_button(self, text, x, y, w, h):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        color = (120, 120, 120) if (x < mouse[0] < x + w and y < mouse[1] < y + h) else (70, 70, 70)

        pygame.draw.rect(self.screen, color, (x, y, w, h), border_radius=12)
        label = self.FONT.render(text, True, (255, 255, 255))
        label_rect = label.get_rect(center=(x + w // 2, y + h // 2))
        self.screen.blit(label, label_rect)

        return click[0] == 1 and x < mouse[0] < x + w and y < mouse[1] < y + h

    # ===============================================
    # Desenare ecrane
    # ===============================================

    def draw_menu(self):
        self.screen.fill((25, 25, 25))
        title = self.FONT.render("IE - Inginerie Electrică", True, (255, 255, 255))
        self.screen.blit(title, (150, 120))

        if self.draw_button("Start Game", 300, 250, 200, 60):
            self.state = self.STATE_GAME
            self.reset_wires()
            self.last_tick = time.time()

    def draw_game(self):
        self.screen.fill((30, 30, 30))

        # Timer update
        now = time.time()
        if now - self.last_tick >= 1:
            self.time_left -= 1
            self.last_tick = now

        # Timer ajunge la 0 -> complete
        if self.time_left <= 0:
            self.state = self.STATE_COMPLETE

        # Timp rămas
        timer_text = self.FONT.render(f"Timp: {int(self.time_left)}", True, (255, 255, 255))
        self.screen.blit(timer_text, (20, 20))

        # Scor curent runda
        score_text = self.FONT.render(f"Scor: {self.round_score}", True, (255, 255, 255))
        self.screen.blit(score_text, (600, 20))

        # Zone target
        for area in self.TARGET_AREAS:
            pygame.draw.rect(self.screen, area["color"], area["rect"])
            label = self.SMALL_FONT.render("Circuit", True, (255, 255, 255))
            self.screen.blit(label, (area["rect"].x + 10, area["rect"].y + 10))

        # Fire
        for w in self.wires:
            pygame.draw.circle(self.screen, w["color"], w["start"], 20)
            if self.dragging == w:
                mx, my = pygame.mouse.get_pos()
                pygame.draw.line(self.screen, w["color"], w["start"], (mx, my), 5)
                pygame.draw.circle(self.screen, w["color"], (mx, my), 15)

        # Dacă toate firele sunt puse → complete
        if all(w["placed"] for w in self.wires):
            # Calculează scorul rundei
            timp_folositor = time.time() - self.round_start_time
            puncte_runda = max(0, int(10 * (self.TIMER_START - timp_folositor)))
            self.round_score = puncte_runda
            self.state = self.STATE_COMPLETE

    def draw_complete(self):
        self.screen.fill((20, 20, 20))

        text = self.FONT.render("Toate circuitele au fost plasate!", True, (0, 255, 0))
        self.screen.blit(text, (100, 180))

        score_text = self.SMALL_FONT.render(f"Scor runda: {self.round_score}", True, (255, 255, 255))
        self.screen.blit(score_text, (100, 260))

        if self.draw_button("Înapoi la meniu", 250, 300, 300, 60):
            self.state = self.STATE_MENU
            # Resetează scorul și timpul pentru următoarea rundă
            self.reset_wires()

    # ===============================================
    # Evenimente pentru fire
    # ===============================================

    def handle_game_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for w in self.wires:
                if not w["placed"]:
                    sx, sy = w["start"]
                    if abs(mx - sx) < 20 and abs(my - sy) < 20:
                        self.dragging = w

        if event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                mx, my = pygame.mouse.get_pos()
                for area in self.TARGET_AREAS:
                    if area["rect"].collidepoint(mx, my) and area["color"] == self.dragging["color"]:
                        self.dragging["start"] = [
                            area["rect"].x + area["rect"].width // 2,
                            area["rect"].y + area["rect"].height // 2
                        ]
                        self.dragging["placed"] = True
                self.dragging = None

    # ===============================================
    # Loop principal
    # ===============================================

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():

                # ESC iese din joc
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

                if event.type == pygame.QUIT:
                    running = False

                if self.state == self.STATE_GAME:
                    self.handle_game_events(event)

            if self.state == self.STATE_MENU:
                self.draw_menu()
            elif self.state == self.STATE_GAME:
                self.draw_game()
            elif self.state == self.STATE_COMPLETE:
                self.draw_complete()

            pygame.display.update()

        pygame.quit()


# Rulează jocul
if __name__ == "__main__":
    IEGame().run()
