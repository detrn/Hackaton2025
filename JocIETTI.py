import pygame
import math
import random


def run_game():
    # --- INITIALIZARE ---
    pygame.init()
    WIDTH, HEIGHT = 1000, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("IETTI: Signal Master - Future Engineer")
    clock = pygame.time.Clock()

    # --- CULORI ---
    BG_COLOR = (10, 15, 30)
    GRID_COLOR = (30, 40, 60)
    NEON_GREEN = (50, 255, 50)
    NEON_RED = (255, 50, 80)
    NEON_BLUE = (0, 200, 255)
    NEON_YELLOW = (255, 230, 0)
    WHITE = (255, 255, 255)

    # --- FONTURI ---
    try:
        font_ui = pygame.font.SysFont("Consolas", 24, bold=True)
        font_big = pygame.font.SysFont("Consolas", 80, bold=True)
    except:
        font_ui = pygame.font.SysFont("Arial", 24, bold=True)
        font_big = pygame.font.SysFont("Arial", 80, bold=True)

    # --- VARIABILE JOC (Definite aici pentru a fi locale funcției) ---
    particles = []
    score = 0
    time_limit = 30
    start_ticks = pygame.time.get_ticks()
    game_active = True

    offset_y = HEIGHT // 2
    phase = 0
    player_amp = 50
    player_freq = 0.04
    target_amp = 100
    target_freq = 0.04
    grid_scroll = 0

    # --- FUNCȚII LOCALE ---
    def create_explosion(x, y, color):
        for _ in range(20):
            particles.append({
                'x': x, 'y': y,
                'vx': random.uniform(-5, 5), 'vy': random.uniform(-5, 5),
                'radius': random.randint(2, 5), 'color': color, 'life': 255
            })

    def update_and_draw_particles(surface):
        for p in particles[:]:
            p['x'] += p['vx'];
            p['y'] += p['vy']
            p['life'] -= 10;
            p['radius'] -= 0.1
            if p['life'] <= 0 or p['radius'] <= 0:
                particles.remove(p);
                continue
            s = pygame.Surface((int(p['radius'] * 2), int(p['radius'] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, p['color'] + (p['life'],), (p['radius'], p['radius']), p['radius'])
            surface.blit(s, (p['x'] - p['radius'], p['y'] - p['radius']))

    def draw_glow_line(surface, color, points, width=2):
        glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        glow_color = color + (50,)
        if len(points) > 1:
            pygame.draw.lines(glow_surf, glow_color, False, points, width + 10)
            pygame.draw.lines(glow_surf, glow_color, False, points, width + 4)
        surface.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        if len(points) > 1:
            pygame.draw.lines(surface, color, False, points, width)

    def draw_grid(surface, offset):
        spacing = 50
        for x in range(0, WIDTH, spacing):
            draw_x = (x - offset) % WIDTH
            pygame.draw.line(surface, GRID_COLOR, (draw_x, 0), (draw_x, HEIGHT), 1)
        for y in range(0, HEIGHT, spacing):
            pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y), 1)
        pygame.draw.line(surface, (50, 60, 80), (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 2)

    def draw_scanlines(surface):
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(surface, (0, 0, 0, 50), (0, y), (WIDTH, y), 1)

    def new_target():
        nonlocal target_amp
        target_amp = random.randint(40, 200)

    def reset_game():
        nonlocal score, start_ticks, game_active, player_amp
        score = 0
        game_active = True
        start_ticks = pygame.time.get_ticks()
        player_amp = 50
        new_target()

    # Inițializare țintă
    new_target()

    # --- BUCLA PRINCIPALĂ ---
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        grid_scroll += 1
        phase += 0.2

        if game_active:
            elapsed = (pygame.time.get_ticks() - start_ticks) / 1000
            time_left = time_limit - elapsed
            if time_left <= 0:
                time_left = 0
                game_active = False
                create_explosion(WIDTH // 2, HEIGHT // 2, NEON_RED)

        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game_active:
                    if event.key == pygame.K_UP: player_amp += 10
                    if event.key == pygame.K_DOWN: player_amp -= 10
                else:
                    if event.key == pygame.K_r: reset_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_active:
                    mx, my = pygame.mouse.get_pos()
                    if my < HEIGHT // 2:
                        player_amp += 10
                    else:
                        player_amp -= 10
                else:
                    reset_game()

        # Desenare
        screen.fill(BG_COLOR)
        draw_grid(screen, grid_scroll)

        points_target = []
        points_player = []
        for x in range(0, WIDTH, 5):
            y_t = offset_y + math.sin((x * target_freq) + phase) * target_amp
            points_target.append((x, y_t))
            y_p = offset_y + math.sin((x * player_freq) + phase) * player_amp
            points_player.append((x, y_p))

        draw_glow_line(screen, NEON_RED, points_target, 3)
        draw_glow_line(screen, NEON_GREEN, points_player, 4)

        if game_active:
            diff = abs(player_amp - target_amp)
            bar_color = NEON_RED if diff > 15 else NEON_GREEN
            pygame.draw.rect(screen, bar_color, (WIDTH - 30, HEIGHT // 2 - diff, 10, diff * 2))

            if diff < 10:
                score += 1
                create_explosion(WIDTH // 2, HEIGHT // 2, NEON_YELLOW)
                create_explosion(WIDTH // 4, HEIGHT // 2, NEON_GREEN)
                create_explosion(3 * WIDTH // 4, HEIGHT // 2, NEON_GREEN)
                new_target()

        update_and_draw_particles(screen)

        # UI
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, WIDTH, 60))
        pygame.draw.line(screen, NEON_BLUE, (0, 60), (WIDTH, 60), 2)

        if game_active:
            lbl_score = font_ui.render(f"SIGNAL LOCKED: {score}", True, NEON_YELLOW)
            screen.blit(lbl_score, (20, 20))

            # Bara Timp
            bar_width = 300
            fill_width = int((time_left / time_limit) * bar_width) if time_limit > 0 else 0
            col_time = NEON_GREEN if time_left > 10 else NEON_RED
            pygame.draw.rect(screen, (50, 50, 50), (WIDTH - 320, 20, bar_width, 20))
            pygame.draw.rect(screen, col_time, (WIDTH - 320, 20, fill_width, 20))
            pygame.draw.rect(screen, WHITE, (WIDTH - 320, 20, bar_width, 20), 2)

            lbl_time = font_ui.render(f"{time_left:.1f}s", True, WHITE)
            screen.blit(lbl_time, (WIDTH - 390, 18))

            lbl_instr = font_ui.render("TAP UP / DOWN to Calibrate", True, (100, 200, 255))
            rect_instr = lbl_instr.get_rect(center=(WIDTH // 2, HEIGHT - 30))
            screen.blit(lbl_instr, rect_instr)
        else:
            s = pygame.Surface((WIDTH, HEIGHT));
            s.set_alpha(200);
            s.fill((0, 0, 0));
            screen.blit(s, (0, 0))
            lbl_go = font_big.render("CONNECTION LOST", True, NEON_RED)
            lbl_final = font_ui.render(f"DATA PACKETS SAVED: {score}", True, NEON_GREEN)
            lbl_rst = font_ui.render(">> PRESS R TO RECONNECT <<", True, WHITE)
            alpha = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 255
            lbl_rst.set_alpha(int(alpha))
            screen.blit(lbl_go, lbl_go.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
            screen.blit(lbl_final, lbl_final.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))
            screen.blit(lbl_rst, lbl_rst.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100)))

        draw_scanlines(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_game()