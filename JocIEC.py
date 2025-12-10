import pygame
import random
import math
import JocIEC
# --- INITIALIZARE SI CONSTANTE (Stil din referinta) ---
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("IEC Hardware Hero: Circuit Catcher")
clock = pygame.time.Clock()

# Culori Neon (Palette din referinta)
BG_COLOR = (10, 15, 30)
GRID_COLOR = (30, 40, 60)
NEON_GREEN = (50, 255, 50)
NEON_RED = (255, 50, 80)
NEON_BLUE = (0, 200, 255)
NEON_YELLOW = (255, 230, 0)
NEON_PURPLE = (180, 50, 255)
WHITE = (255, 255, 255)

# Fonturi "Tech"
try:
    font_ui = pygame.font.SysFont("Consolas", 24, bold=True)
    font_big = pygame.font.SysFont("Consolas", 80, bold=True)
    font_small = pygame.font.SysFont("Consolas", 16, bold=True)
except:
    font_ui = pygame.font.SysFont("Arial", 24, bold=True)
    font_big = pygame.font.SysFont("Arial", 80, bold=True)
    font_small = pygame.font.SysFont("Arial", 16, bold=True)

# --- SISTEM DE PARTICULE (Din referinta) ---
particles = []


def create_explosion(x, y, color):
    for _ in range(25):
        particles.append({
            'x': x, 'y': y,
            'vx': random.uniform(-6, 6), 'vy': random.uniform(-6, 6),
            'radius': random.randint(3, 7),
            'color': color, 'life': 255
        })


def update_and_draw_particles(surface):
    for p in particles[:]:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['life'] -= 8
        p['radius'] -= 0.1
        if p['life'] <= 0 or p['radius'] <= 0:
            particles.remove(p)
            continue
        # Desenare cu efect de glow (folosind additive blending pe o suprafata temporara)
        s = pygame.Surface((int(p['radius'] * 4), int(p['radius'] * 4)), pygame.SRCALPHA)
        pygame.draw.circle(s, p['color'] + (100,), (p['radius'] * 2, p['radius'] * 2), p['radius'] * 1.5)
        surface.blit(s, (p['x'] - p['radius'] * 2, p['y'] - p['radius'] * 2), special_flags=pygame.BLEND_RGBA_ADD)


# --- FUNCTII GRAFICE AUXILIARE (Stil din referinta) ---

# Functie noua: Aplica efectul de "glow" pe un dreptunghi (adaptat din draw_glow_line)
def draw_neon_rect(surface, color, rect, thickness=2, fill=False):
    # Aura strălucitoare (groasă, transparentă, additive blend)
    glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf, color + (60,), rect.inflate(12, 12), thickness + 6)
    pygame.draw.rect(glow_surf, color + (100,), rect.inflate(6, 6), thickness + 3)
    surface.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Miezul solid
    if fill:
        pygame.draw.rect(surface, color, rect)
    else:
        pygame.draw.rect(surface, color, rect, thickness)


def draw_grid(surface, scroll_y):
    spacing = 60
    # Linii verticale
    for x in range(0, WIDTH, spacing):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
    # Linii orizontale care se misca in jos
    for y in range(-spacing, HEIGHT, spacing):
        draw_y = (y + scroll_y) % (HEIGHT + spacing)
        pygame.draw.line(surface, GRID_COLOR, (0, draw_y), (WIDTH, draw_y), 1)


def draw_scanlines(surface):
    for y in range(0, HEIGHT, 4):
        pygame.draw.line(surface, (0, 0, 0, 70), (0, y), (WIDTH, y), 1)


# --- CLASELE JOCULUI ---

class PlayerSocket:
    def __init__(self):
        self.width = 100
        self.height = 30
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 60
        self.speed = 9
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.glow_phase = 0

    def move(self, dx):
        self.x += dx
        self.x = max(0, min(WIDTH - self.width, self.x))
        self.rect.x = self.x

    def draw(self, surface):
        self.glow_phase += 0.1
        # Pulsatie a culorii albastre
        pulse_val = abs(math.sin(self.glow_phase)) * 55
        current_color = (NEON_BLUE[0], min(255, NEON_BLUE[1] + pulse_val), min(255, NEON_BLUE[2] + pulse_val))

        # Desenam soclul cu glow
        draw_neon_rect(surface, current_color, self.rect, 3)
        # Detalii pini
        for i in range(self.rect.left + 10, self.rect.right - 10, 15):
            pygame.draw.line(surface, current_color, (i, self.rect.top), (i, self.rect.bottom), 2)


class FallingComponent:
    def __init__(self):
        self.type = random.choice(['CPU', 'RAM', 'CAP', 'WATER', 'FIRE', 'ESD'])
        self.is_bad = self.type in ['WATER', 'FIRE', 'ESD']

        # Dimensiuni si culori in functie de tip
        if self.type == 'CPU':
            self.width, self.height = 50, 50
            self.color = NEON_YELLOW
            self.speed = random.uniform(3, 5)
        elif self.type == 'RAM':
            self.width, self.height = 70, 20
            self.color = NEON_GREEN
            self.speed = random.uniform(4, 6)
        elif self.type == 'CAP':  # Condensator
            self.width, self.height = 25, 35
            self.color = NEON_PURPLE
            self.speed = random.uniform(3, 5)
        elif self.type == 'WATER':
            self.width, self.height = 30, 40
            self.color = NEON_BLUE  # Albastru dar rau
            self.speed = random.uniform(5, 7)
        elif self.type == 'FIRE':
            self.width, self.height = 40, 40
            self.color = NEON_RED
            self.speed = random.uniform(4, 6)
        elif self.type == 'ESD':  # Electrostatic Discharge
            self.width, self.height = 30, 50
            self.color = (255, 100, 100)  # Rosu deschis
            self.speed = random.uniform(6, 8)

        self.x = random.randint(20, WIDTH - self.width - 20)
        self.y = -self.height - random.randint(0, 100)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, surface):
        # Desenare specifica fiecarui tip, mentinand stilul NEON GLOW
        if self.type == 'CPU':
            draw_neon_rect(surface, self.color, self.rect, 3)
            # Un mic patrat in mijloc
            draw_neon_rect(surface, self.color, self.rect.inflate(-20, -20), 1, fill=True)

        elif self.type == 'RAM':
            draw_neon_rect(surface, self.color, self.rect, 2)
            # Chipuri mici negre pe el
            for i in range(3):
                chip_rect = pygame.Rect(self.x + 5 + i * 22, self.y + 5, 15, 10)
                pygame.draw.rect(surface, BG_COLOR, chip_rect)

        elif self.type == 'CAP':
            # Desenam ca un cilindru stilizat
            top_rect = pygame.Rect(self.x, self.y, self.width, 10)
            body_rect = pygame.Rect(self.x + 5, self.y + 10, self.width - 10, self.height - 10)
            draw_neon_rect(surface, self.color, top_rect, 2)
            draw_neon_rect(surface, self.color, body_rect, 2, fill=True)

        elif self.type == 'WATER':
            # Forma de picatura stilizata neon
            pts = [(self.x + self.width // 2, self.y), (self.x, self.y + self.height),
                   (self.x + self.width, self.y + self.height)]
            glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(glow_surf, self.color + (80,), pts, 8)
            surface.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            pygame.draw.polygon(surface, self.color, pts, 3)

        elif self.type == 'FIRE':
            # Cerc neregulat neon
            glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, self.color + (80,), self.rect.center, self.width // 2 + 5)
            surface.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            pygame.draw.circle(surface, NEON_YELLOW, self.rect.center, self.width // 2 - 5)  # Miez galben

        elif self.type == 'ESD':
            # Linie zigzag (fulger)
            pts = [(self.x + self.width // 2, self.y), (self.x, self.y + self.height // 2),
                   (self.x + self.width, self.y + self.height // 2), (self.x + self.width // 2, self.y + self.height)]

            glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.lines(glow_surf, self.color + (80,), False, pts, 8)
            surface.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            pygame.draw.lines(surface, WHITE, False, pts, 3)

        # Eticheta text mica pentru claritate
        lbl = font_small.render(self.type, True, self.color)
        surface.blit(lbl, (self.x, self.y - 15))


# --- LOGICA JOCULUI ---
player = PlayerSocket()
components = []
score = 0
lives = 3
game_active = True
grid_scroll_y = 0
spawn_timer = 0


def reset_game():
    global score, lives, game_active, components, player, spawn_timer
    score = 0
    lives = 3
    game_active = True
    components = []
    player = PlayerSocket()
    spawn_timer = 0


# --- BUCLA PRINCIPALA ---
running = True
while running:
    dt = clock.tick(60)
    grid_scroll_y += 2  # Viteza grila fundal

    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if not game_active and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            reset_game()

    # 2. Game Logic
    if game_active:
        # Miscare jucator
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: player.move(-player.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player.move(player.speed)

        # Spawning componente
        spawn_timer += 1
        if spawn_timer >= 50:  # Rata de aparitie
            components.append(FallingComponent())
            spawn_timer = 0
            # Crestem dificultatea usor in timp
            if spawn_timer > 20 and score > 1000: spawn_timer = 20

        # Update componente
        for comp in components[:]:
            comp.update()

            # Coliziune cu jucatorul
            if comp.rect.colliderect(player.rect):
                create_explosion(comp.rect.centerx, comp.rect.centery, comp.color)
                if not comp.is_bad:
                    score += 100
                else:
                    lives -= 1
                    # Flash rosu pe ecran la damage
                    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    s.fill(NEON_RED + (100,))
                    screen.blit(s, (0, 0))

                components.remove(comp)

            # Iesire din ecran
            elif comp.y > HEIGHT:
                components.remove(comp)
                if not comp.is_bad:  # Penalizare daca scapi componente bune
                    score = max(0, score - 10)

        if lives <= 0:
            game_active = False
            create_explosion(player.rect.centerx, player.rect.centery, NEON_BLUE)

    # 3. Desenare
    screen.fill(BG_COLOR)
    draw_grid(screen, grid_scroll_y)

    if game_active:
        player.draw(screen)
        for comp in components:
            comp.draw(screen)

    update_and_draw_particles(screen)

    # --- INTERFATA (HUD) - Stil din referinta ---
    # Bara de sus
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, WIDTH, 60))
    pygame.draw.line(screen, NEON_BLUE, (0, 60), (WIDTH, 60), 2)

    if game_active:
        # Scor
        lbl_score = font_ui.render(f"HARDWARE COLLECTED: {score}", True, NEON_YELLOW)
        screen.blit(lbl_score, (20, 20))

        # Vieti (Integrity)
        colors_lives = [NEON_RED, NEON_YELLOW, NEON_GREEN, NEON_GREEN]
        lbl_lives = font_ui.render(f"SYSTEM INTEGRITY: {lives * 33}%", True, colors_lives[lives])
        screen.blit(lbl_lives, (WIDTH - 320, 20))

    else:
        # Game Over Screen - Stil din referinta
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(220)
        s.fill((0, 0, 0))
        screen.blit(s, (0, 0))

        lbl_go = font_big.render("SYSTEM FAILURE", True, NEON_RED)
        lbl_final = font_ui.render(f"TOTAL COMPONENTS: {score}", True, NEON_GREEN)
        lbl_rst = font_ui.render(">> PRESS R TO REBOOT SYSTEM <<", True, WHITE)

        # Efect de pulsare
        alpha = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 255
        lbl_rst.set_alpha(int(alpha))

        screen.blit(lbl_go, lbl_go.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
        screen.blit(lbl_final, lbl_final.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))
        screen.blit(lbl_rst, lbl_rst.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100)))

    # Efect final: Scanlines (peste tot)
    draw_scanlines(screen)

    pygame.display.flip()

pygame.quit()