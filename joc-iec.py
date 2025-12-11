import pygame
import math
import random
import sys

# ----------------------------
# Signal Engineer - PCB Repair
# ----------------------------
# Instrucțiuni:
#   Up / Down    -> mărește / micșorează amplitudinea
#   Left / Right -> mărește / micșorează frecvența
#   Space        -> power on/off
#   Click mouse  -> repară (sudură) componentele defecte
#   R            -> restart
#
# Scop: potrivește semnalul (amplitudine + frecvență) cu ținta circuitului
#       pentru a alimenta componentele fără supraîncălzire.

pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Signal Engineer - PCB Repair")
clock = pygame.time.Clock()

# Culori
BG_COLOR = (8, 12, 20)
GRID_COLOR = (26, 34, 48)
NEON_GREEN = (50, 255, 90)
NEON_RED = (255, 80, 90)
NEON_BLUE = (0, 200, 255)
NEON_YELLOW = (255, 230, 0)
WHITE = (230, 230, 230)
METAL = (80, 88, 98)

# Fonturi
try:
    font_ui = pygame.font.SysFont("Consolas", 20, bold=True)
    font_big = pygame.font.SysFont("Consolas", 64, bold=True)
except:
    font_ui = pygame.font.SysFont("Arial", 20, bold=True)
    font_big = pygame.font.SysFont("Arial", 64, bold=True)

# Particule pentru "sudură / spark"
particles = []
def create_sparks(x, y, color, n=15):
    for _ in range(n):
        particles.append({
            'x': x + random.uniform(-6, 6),
            'y': y + random.uniform(-6, 6),
            'vx': random.uniform(-3, 3),
            'vy': random.uniform(-3, 3),
            'radius': random.uniform(2, 5),
            'color': color,
            'life': random.randint(40, 100)
        })

def update_and_draw_particles(surface):
    for p in particles[:]:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['life'] -= 4
        p['radius'] *= 0.98
        if p['life'] <= 0 or p['radius'] <= 0.5:
            particles.remove(p)
            continue
        s = pygame.Surface((int(p['radius']*2)+2, int(p['radius']*2)+2), pygame.SRCALPHA)
        col = p['color'] + (min(255, max(0, p['life']*2)),)
        pygame.draw.circle(s, col, (int(p['radius']), int(p['radius'])), int(p['radius']))
        surface.blit(s, (p['x']-p['radius'], p['y']-p['radius']), special_flags=pygame.BLEND_ADD)

# Efect strălucire linie
def draw_glow_line(surface, color, points, width=2):
    glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    glow_color = color + (60,)
    if len(points) > 1:
        pygame.draw.lines(glow_surf, glow_color, False, points, width + 10)
        pygame.draw.lines(glow_surf, glow_color, False, points, width + 4)
    surface.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    if len(points) > 1:
        pygame.draw.lines(surface, color, False, points, width)

# Grid / PCB look
def draw_grid(surface, offset):
    spacing = 40
    for x in range(-offset % spacing, WIDTH, spacing):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, spacing):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y), 1)
    # silkscreen center
    pygame.draw.rect(surface, (30, 35, 45), (20, 80, WIDTH-40, HEIGHT-160), border_radius=6)

# Component class
class Component:
    def __init__(self, x, y, w, h, name):
        self.rect = pygame.Rect(x, y, w, h)
        self.name = name
        self.healthy = True
        self.heat = 0.0  # 0..100
        self.fail_timer = 0

    def draw(self, surface):
        # body
        body_col = METAL if self.healthy else (70, 30, 30)
        pygame.draw.rect(surface, body_col, self.rect, border_radius=4)
        # label
        lbl = font_ui.render(self.name, True, WHITE)
        surface.blit(lbl, (self.rect.x + 6, self.rect.y + 6))
        # heat bar
        hb = pygame.Rect(self.rect.x, self.rect.bottom - 8, self.rect.w * (self.heat / 100), 6)
        pygame.draw.rect(surface, NEON_RED if self.heat>75 else NEON_YELLOW if self.heat>40 else NEON_GREEN, hb)
        pygame.draw.rect(surface, (40,40,40), (self.rect.x, self.rect.bottom - 8, self.rect.w, 6), 2)

    def update(self, power_on, input_level, dt):
        # Dacă e defectă, heat crește mai mult la alimentare
        if power_on:
            heat_increase = (abs(input_level) / 200.0) * (2.0 if not self.healthy else 0.6)
            self.heat += heat_increase * dt * 60
        else:
            self.heat -= 0.8 * dt * 60
        self.heat = max(0, min(100, self.heat))

        # dacă prea fierbinte -> devine defect
        if self.heat >= 100 and self.healthy:
            self.healthy = False
            self.fail_timer = pygame.time.get_ticks()
            create_sparks(self.rect.centerx, self.rect.centery, NEON_RED, n=30)

        # random failure chance
        if self.healthy and random.random() < 0.0006:
            # degrade a little
            self.healthy = False
            create_sparks(self.rect.centerx, self.rect.centery, NEON_YELLOW, n=12)

    def click_repair(self):
        # Repară componenta
        if not self.healthy:
            self.healthy = True
            self.heat = max(10, self.heat - random.uniform(20, 50))
            create_sparks(self.rect.centerx, self.rect.centery, NEON_GREEN, n=18)
            return True
        # small solder spark effect even if not needed
        create_sparks(self.rect.centerx, self.rect.centery, NEON_BLUE, n=6)
        return False

# Game logic / state
score = 0
time_limit = 45.0
start_ticks = 0
game_active = True

offset_y = HEIGHT//2 + 40
phase = 0.0

# Player source
player_amp = 60
player_freq = 0.035
power_on = True

# Target circuit (tensiune țintă) - amplitudine țintă
target_amp = random.randint(40, 180)
target_freq = random.uniform(0.02, 0.07)
def new_target():
    global target_amp, target_freq
    target_amp = random.randint(40, 200)
    target_freq = random.uniform(0.02, 0.07)

def reset_game():
    global score, start_ticks, game_active, player_amp, player_freq, power_on, components
    score = 0
    game_active = True
    start_ticks = pygame.time.get_ticks()
    player_amp = 60
    player_freq = 0.035
    power_on = True
    new_target()
    # Components layout
    components = [
        Component(80, 150, 140, 70, "CPU"),
        Component(260, 150, 140, 70, "VRM"),
        Component(440, 150, 140, 70, "RAM"),
        Component(620, 150, 140, 70, "USB"),
        Component(800, 150, 140, 70, "AUDIO"),
        Component(260, 340, 140, 70, "SENSOR"),
        Component(440, 340, 140, 70, "ADC"),
        Component(620, 340, 140, 70, "DAC"),
    ]
    # some components start damaged randomly
    for c in components:
        if random.random() < 0.15:
            c.healthy = False
            c.heat = random.uniform(30, 70)

reset_game()

# main loop
running = True
grid_scroll = 0
while running:
    dt = clock.tick(60) / 1000.0
    phase += 0.18
    grid_scroll += 1

    # timing
    if game_active:
        elapsed = (pygame.time.get_ticks() - start_ticks) / 1000.0
        time_left = time_limit - elapsed
        if time_left <= 0:
            time_left = 0
            game_active = False
            create_sparks(WIDTH//2, HEIGHT//2, NEON_RED, n=60)

    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player_amp += 10
            if event.key == pygame.K_DOWN:
                player_amp -= 10
            if event.key == pygame.K_LEFT:
                player_freq = max(0.005, player_freq - 0.005)
            if event.key == pygame.K_RIGHT:
                player_freq += 0.005
            if event.key == pygame.K_SPACE:
                power_on = not power_on
            if event.key == pygame.K_r and not game_active:
                reset_game()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if game_active:
                # click components to repair
                for c in components:
                    if c.rect.collidepoint(mx, my):
                        repaired = c.click_repair()
                        if repaired:
                            score += 2
            else:
                reset_game()

    # clamp player amp
    player_amp = max(0, min(300, player_amp))

    # draw
    screen.fill(BG_COLOR)
    draw_grid(screen, grid_scroll)

    # desenare "placa" (pcb)
    pcb_rect = pygame.Rect(40, 80, WIDTH-80, HEIGHT-160)
    pygame.draw.rect(screen, (12, 18, 28), pcb_rect, border_radius=6)
    pygame.draw.rect(screen, (18, 26, 36), pcb_rect.inflate(-8, -8), 2, border_radius=6)

    # update & draw components
    input_level = player_amp if power_on else 0
    for c in components:
        c.update(power_on, input_level, dt)
        c.draw(screen)

    # calcul semnale (puncte)
    points_target = []
    points_player = []
    for x in range(0, WIDTH, 4):
        y_t = offset_y + math.sin((x * target_freq) + phase) * target_amp
        points_target.append((x, y_t))
        y_p = offset_y + math.sin((x * player_freq) + phase) * player_amp
        points_player.append((x, y_p))

    # desen semnale
    draw_glow_line(screen, NEON_RED, points_target, 3)
    draw_glow_line(screen, NEON_GREEN, points_player, 3)

    # verificare sincronizare cu "circuit"
    if game_active and power_on:
        amp_diff = abs(player_amp - target_amp)
        freq_diff = abs(player_freq - target_freq)
        # un scor e obtinut daca atat amplitudinea cat si frecventa sunt suficient de aproape
        if amp_diff < 12 and freq_diff < 0.007:
            # successful "lock"
            score += 1
            create_sparks(WIDTH//2, HEIGHT//2, NEON_YELLOW, n=18)
            new_target()

    # afișare UI sus
    ui_h = 72
    pygame.draw.rect(screen, (6, 8, 12), (0, 0, WIDTH, ui_h))
    pygame.draw.line(screen, NEON_BLUE, (0, ui_h), (WIDTH, ui_h), 2)

    lbl_title = font_ui.render("Signal Engineer - PCB Repair", True, NEON_BLUE)
    screen.blit(lbl_title, (18, 14))

    lbl_score = font_ui.render(f"DATA PACKETS: {score}", True, NEON_YELLOW)
    screen.blit(lbl_score, (220, 14))

    # power indicator
    power_col = NEON_GREEN if power_on else (80, 80, 80)
    pygame.draw.circle(screen, power_col, (WIDTH-60, 36), 12)
    lbl_power = font_ui.render("POWER", True, WHITE)
    screen.blit(lbl_power, (WIDTH-110, 14))

    # timer bar
    if game_active:
        bar_w = 320
        fill = int(((time_left) / time_limit) * bar_w)
        pygame.draw.rect(screen, (30, 30, 30), (WIDTH//2 - bar_w//2, 16, bar_w, 18))
        pygame.draw.rect(screen, NEON_GREEN if time_left>12 else NEON_RED, (WIDTH//2 - bar_w//2, 16, fill, 18))
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - bar_w//2, 16, bar_w, 18), 2)
        lbl_time = font_ui.render(f"{time_left:.1f}s", True, WHITE)
        screen.blit(lbl_time, (WIDTH//2 + bar_w//2 + 6, 12))
    else:
        lbl_dead = font_big.render("SYSTEM OFFLINE", True, NEON_RED)
        screen.blit(lbl_dead, lbl_dead.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
        lbl_final = font_ui.render(f"PACKETS SAVED: {score}", True, NEON_GREEN)
        screen.blit(lbl_final, lbl_final.get_rect(center=(WIDTH//2, HEIGHT//2 + 30)))
        lbl_rst = font_ui.render(">> PRESS R TO REBOOT <<", True, WHITE)
        alpha = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 255
        lbl_rst.set_alpha(int(alpha))
        screen.blit(lbl_rst, lbl_rst.get_rect(center=(WIDTH//2, HEIGHT//2 + 80)))

    # afișare "multimetru" lateral
    meter_x = WIDTH - 220
    meter_y = 100
    pygame.draw.rect(screen, (10, 12, 14), (meter_x, meter_y, 200, 260), border_radius=8)
    pygame.draw.rect(screen, (22, 28, 36), (meter_x+8, meter_y+8, 184, 244), border_radius=6)
    # player values
    lbl_a = font_ui.render(f"Vout: {player_amp} mV", True, NEON_GREEN if abs(player_amp-target_amp)<12 else WHITE)
    screen.blit(lbl_a, (meter_x+16, meter_y+18))
    lbl_f = font_ui.render(f"Freq: {player_freq:.3f} kHz", True, NEON_GREEN if abs(player_freq-target_freq)<0.007 else WHITE)
    screen.blit(lbl_f, (meter_x+16, meter_y+48))
    lbl_tgt = font_ui.render(f"Target V: {target_amp} mV", True, NEON_RED)
    screen.blit(lbl_tgt, (meter_x+16, meter_y+84))
    lbl_tgf = font_ui.render(f"Target F: {target_freq:.3f} kHz", True, NEON_RED)
    screen.blit(lbl_tgf, (meter_x+16, meter_y+112))

    # draw LED row showing component health
    led_y = meter_y + 150
    px = meter_x + 18
    for c in components[:5]:
        led_col = NEON_GREEN if c.healthy and c.heat<70 else NEON_YELLOW if c.healthy else NEON_RED
        pygame.draw.circle(screen, led_col, (px, led_y), 10)
        lblc = font_ui.render(c.name, True, WHITE)
        screen.blit(lblc, (px+20, led_y-10))
        led_y += 28

    # draw heat map at bottom
    for c in components[5:]:
        led_col = NEON_GREEN if c.healthy and c.heat<70 else NEON_YELLOW if c.healthy else NEON_RED
        pygame.draw.circle(screen, led_col, (px+120, meter_y+150 + (components.index(c)-5)*28), 10)
        lblc = font_ui.render(c.name, True, WHITE)
        screen.blit(lblc, (px+140, meter_y+150 + (components.index(c)-5)*28 - 10))

    # desenare bare / indicatori suplimentari
    # heat overlay on PCB: subtle glow near hot components
    for c in components:
        if c.heat > 40:
            glow = pygame.Surface((c.rect.w+20, c.rect.h+20), pygame.SRCALPHA)
            intensity = int((c.heat/100.0) * 80)
            col = (255, 80, 60, intensity) if not c.healthy else (255, 200, 80, int(intensity*0.6))
            pygame.draw.ellipse(glow, col, glow.get_rect())
            screen.blit(glow, (c.rect.x-10, c.rect.y-10), special_flags=pygame.BLEND_RGB_ADD)

    # scanlines
    for y in range(0, HEIGHT, 4):
        sline = pygame.Surface((WIDTH,1), pygame.SRCALPHA)
        sline.fill((0,0,0,20))
        screen.blit(sline, (0,y))

    # particule
    update_and_draw_particles(screen)

    # mici instructiuni jos
    lbl_instr = font_ui.render("UP/DOWN amplitude  LEFT/RIGHT freq  SPACE power  CLICK repair", True, (160,200,255))
    screen.blit(lbl_instr, (20, HEIGHT-34))

    pygame.display.flip()

pygame.quit()
sys.exit()
