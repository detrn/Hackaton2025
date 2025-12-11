import pygame
import random
import math

# Jocul a fost re-scris ca un singur script pentru simplitate si concizie.

# --- INITIALIZARE SI CONSTANTE ---
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RPi Circuit Catcher - Touch LITE")
clock = pygame.time.Clock()

# Culori Simplistice
BG_COLOR = (10, 15, 30)
NEON_GREEN = (50, 255, 50)
NEON_RED = (255, 50, 80)
NEON_BLUE = (0, 150, 255)
NEON_YELLOW = (255, 230, 0)
NEON_PURPLE = (180, 50, 255)
WHITE = (255, 255, 255)
# Fonturi (pentru compatibilitate maxima pe RPi)
font_ui = pygame.font.Font(None, 36)
font_big = pygame.font.Font(None, 100)


# --- CLASELE JOCULUI (Fara modificari substantiale) ---

class PlayerSocket:
    def __init__(self):
        self.width, self.height = 100, 30
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 60
        self.speed = 9
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.color = NEON_BLUE

    def move_to(self, target_x):
        # Muta socket-ul catre pozitia X a atingerii/mouse-ului
        center_x = self.x + self.width // 2

        # Calculeaza directia si limiteaza miscarea la speed
        if target_x < center_x - 5:
            dx = -min(self.speed, center_x - target_x)
        elif target_x > center_x + 5:
            dx = min(self.speed, target_x - center_x)
        else:
            dx = 0

        self.x = max(0, min(WIDTH - self.width, self.x + dx))
        self.rect.x = self.x

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, 0)
        for i in range(self.rect.left + 10, self.rect.right - 10, 15):
            pygame.draw.line(surface, WHITE, (i, self.rect.top), (i, self.rect.bottom), 2)


class FallingComponent:
    def __init__(self):
        self.type = random.choice(['CPU', 'RAM', 'CAP', 'WATER', 'FIRE', 'ESD'])
        self.is_bad = self.type in ['WATER', 'FIRE', 'ESD']

        self.width, self.height, self.color, self.speed = self._set_properties()

        self.x = random.randint(20, WIDTH - self.width - 20)
        self.y = -self.height - random.randint(0, 100)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def _set_properties(self):
        if self.type == 'CPU': return 50, 50, NEON_YELLOW, random.uniform(3, 5)
        if self.type == 'RAM': return 70, 20, NEON_GREEN, random.uniform(4, 6)
        if self.type == 'CAP': return 25, 35, NEON_PURPLE, random.uniform(3, 5)
        if self.type == 'WATER': return 30, 40, NEON_BLUE, random.uniform(5, 7)
        if self.type == 'FIRE': return 40, 40, NEON_RED, random.uniform(4, 6)
        if self.type == 'ESD': return 30, 50, (255, 100, 100), random.uniform(6, 8)
        return 30, 30, WHITE, 4

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, surface):
        if self.type in ['CPU', 'RAM', 'CAP']:
            pygame.draw.rect(surface, self.color, self.rect, 2)
        elif self.type == 'WATER':
            pts = [(self.x + self.width // 2, self.y), (self.x, self.y + self.height),
                   (self.x + self.width, self.y + self.height)]
            pygame.draw.polygon(surface, self.color, pts, 0)
        elif self.type == 'FIRE':
            pygame.draw.circle(surface, self.color, self.rect.center, self.width // 2, 0)
        elif self.type == 'ESD':
            pts = [(self.x + self.width // 2, self.y), (self.x, self.y + self.height // 2),
                   (self.x + self.width, self.y + self.height // 2), (self.x + self.width // 2, self.y + self.height)]
            pygame.draw.lines(surface, WHITE, False, pts, 3)

        lbl = font_ui.render(self.type[0], True, self.color)
        surface.blit(lbl, self.rect.center)


# --- LOGICA JOCULUI ---
player = PlayerSocket()
components = []
score, lives, game_active = 0, 3, True
spawn_timer = 0
# Variabila noua pentru controlul touch/mouse
target_x_position = player.x + player.width // 2


def reset_game():
    global score, lives, game_active, components, player, spawn_timer, target_x_position
    score, lives, game_active = 0, 3, True
    components, player, spawn_timer = [], PlayerSocket(), 0
    target_x_position = player.x + player.width // 2


def draw_ui():
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, WIDTH, 40))
    pygame.draw.line(screen, NEON_BLUE, (0, 40), (WIDTH, 40), 2)

    lbl_score = font_ui.render(f"SCORE: {score}", True, NEON_YELLOW)
    screen.blit(lbl_score, (20, 10))

    colors_lives = [NEON_RED, NEON_YELLOW, NEON_GREEN, NEON_GREEN]
    lbl_lives = font_ui.render(f"LIVES: {lives}", True, colors_lives[lives])
    screen.blit(lbl_lives, (WIDTH - 150, 10))


def draw_game_over():
    s = pygame.Surface((WIDTH, HEIGHT))
    s.set_alpha(200)
    s.fill((0, 0, 0))
    screen.blit(s, (0, 0))

    lbl_go = font_big.render("GAME OVER", True, NEON_RED)
    lbl_final = font_ui.render(f"FINAL SCORE: {score}", True, NEON_GREEN)
    lbl_rst = font_ui.render("PRESS R / TOUCH TO RESTART", True, WHITE)  # Moficiat pentru touch

    screen.blit(lbl_go, lbl_go.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
    screen.blit(lbl_final, lbl_final.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))
    screen.blit(lbl_rst, lbl_rst.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80)))


# --- BUCLA PRINCIPALA ---
running = True
while running:
    clock.tick(60)

    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

        # Daca jocul nu e activ, detectam restart-ul prin tasta R SAU mouse/touch
        if not game_active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:  # Touch/Mouse Click
                reset_game()

        # Controlul jucatorului prin touch/mouse
        if game_active:
            if event.type == pygame.MOUSEMOTION:  # Mouse Miscat (drag)
                target_x_position = event.pos[0]
            if event.type == pygame.MOUSEBUTTONDOWN:  # Click / Touch Start
                target_x_position = event.pos[0]

            # Pe Raspberry Pi, FINGERMOTION si FINGERDOWN sunt evenimentele de touch
            if event.type == pygame.FINGERMOTION or event.type == pygame.FINGERDOWN:
                # Coordonatele FINGER vin normalizate (0.0 la 1.0)
                target_x_position = event.x * WIDTH

                # 2. Game Logic
    if game_active:
        # Miscare jucator catre pozitia touch/mouse
        player.move_to(target_x_position)

        # Spawning
        spawn_timer += 1
        if spawn_timer >= 50 - min(40, score // 500):
            components.append(FallingComponent())
            spawn_timer = 0

        # Update & Coliziune
        for comp in components[:]:
            comp.update()

            if comp.rect.colliderect(player.rect):
                if not comp.is_bad:
                    score += 100
                else:
                    lives -= 1
                components.remove(comp)

            elif comp.y > HEIGHT:
                components.remove(comp)
                if not comp.is_bad: score = max(0, score - 10)

        if lives <= 0: game_active = False

    # 3. Desenare
    screen.fill(BG_COLOR)

    if game_active:
        player.draw(screen)
        for comp in components: comp.draw(screen)

    draw_ui()
    if not game_active: draw_game_over()

    pygame.display.flip()

pygame.quit()