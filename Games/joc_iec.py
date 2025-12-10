import pygame
import random
import math

# --- CONFIGURARE ---
WIDTH, HEIGHT = 800, 600
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("IEC: Hardware Hero - Circuit Builder")
clock = pygame.time.Clock()

# --- CULORI (TEMATICĂ PCB) ---
PCB_GREEN = (0, 100, 0)       # Verde închis (Placă)
TRACE_GREEN = (0, 180, 0)     # Verde deschis (Trasee)
GREEN = (0, 255, 0)           # Verde standard
BLUE = (0, 120, 255)          # <--- ADAUGĂ ACEASTA LINIE (Albastru)
SILVER = (192, 192, 192)      # Pini / Lipituri
BLACK = (20, 20, 20)          # Cipuri
GOLD = (218, 165, 32)         # Contacte aurite
RED = (255, 50, 50)           # Pericol
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)          # Energie

# Fonturi
try:
    font_ui = pygame.font.SysFont("Consolas", 20, bold=True)
    font_big = pygame.font.SysFont("Consolas", 60, bold=True)
except:
    font_ui = pygame.font.SysFont("Arial", 20, bold=True)
    font_big = pygame.font.SysFont("Arial", 60, bold=True)


# --- GENERARE FUNDAL PCB (Procedural) ---
def create_pcb_background():
    """Creează o imagine statică cu trasee de circuite."""
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill(PCB_GREEN)

    # Desenăm trasee random
    for _ in range(50):
        start_x = random.randint(0, WIDTH)
        start_y = random.randint(0, HEIGHT)
        end_x = start_x + random.choice([-100, 0, 100])
        end_y = start_y + random.choice([-100, 0, 100])

        # Linie traseu
        pygame.draw.line(bg, TRACE_GREEN, (start_x, start_y), (end_x, end_y), 3)
        # Cerc la capete (via)
        pygame.draw.circle(bg, SILVER, (start_x, start_y), 5)
        pygame.draw.circle(bg, SILVER, (end_x, end_y), 5)

    return bg


bg_surface = create_pcb_background()


# --- CLASE ---

class Player:
    def __init__(self):
        self.width = 80
        self.height = 20
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 50
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = 8

    def move(self, dx):
        self.x += dx
        # Limite ecran
        if self.x < 0: self.x = 0
        if self.x > WIDTH - self.width: self.x = WIDTH - self.width
        self.rect.x = self.x

    def draw(self, surface):
        # Desenăm Soclul (Socket)
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=5)
        # Pini interiori
        for i in range(0, self.width, 10):
            pygame.draw.circle(surface, BLACK, (self.rect.x + 5 + i, self.rect.y + 5), 2)
            pygame.draw.circle(surface, BLACK, (self.rect.x + 5 + i, self.rect.y + 15), 2)
        # Text "SOCKET"
        text = font_ui.render("SOCKET", True, BLACK)
        # surface.blit(text, (self.rect.x + 5, self.rect.y - 20))


class FallingItem:
    def __init__(self):
        self.x = random.randint(20, WIDTH - 50)
        self.y = -50
        self.speed = random.randint(3, 7)
        self.type = random.choice([
            "CPU", "RAM", "RESISTOR", "CAPACITOR", "FPGA",  # Bune
            "WATER", "FIRE", "ESD"  # Rele
        ])

        # Setări în funcție de tip
        if self.type in ["WATER", "FIRE", "ESD"]:
            self.is_good = False
        else:
            self.is_good = True

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        # Desenăm grafică procedurală în funcție de componentă
        if self.type == "CPU":
            # Pătrat gri cu pini aurii
            r = pygame.Rect(self.x, self.y, 40, 40)
            pygame.draw.rect(surface, SILVER, r)
            pygame.draw.rect(surface, (100, 100, 100), r.inflate(-10, -10))
            # Text mic
            l = pygame.font.SysFont("Arial", 10).render("INTEL", True, WHITE)
            surface.blit(l, (self.x + 5, self.y + 15))

        elif self.type == "RAM":
            # Dreptunghi verde lung
            r = pygame.Rect(self.x, self.y, 60, 20)
            pygame.draw.rect(surface, (0, 200, 0), r)
            # Cipuri negre
            pygame.draw.rect(surface, BLACK, (self.x + 5, self.y + 5, 10, 10))
            pygame.draw.rect(surface, BLACK, (self.x + 25, self.y + 5, 10, 10))
            pygame.draw.rect(surface, BLACK, (self.x + 45, self.y + 5, 10, 10))

        elif self.type == "FPGA":
            # Pătrat mare negru (Xilinx style)
            r = pygame.Rect(self.x, self.y, 50, 50)
            pygame.draw.rect(surface, BLACK, r)
            pygame.draw.rect(surface, SILVER, r, 2)
            l = pygame.font.SysFont("Arial", 12, bold=True).render("FPGA", True, WHITE)
            surface.blit(l, (self.x + 10, self.y + 18))

        elif self.type == "RESISTOR":
            # Cilindru bej cu dungi
            pygame.draw.rect(surface, (245, 245, 220), (self.x, self.y, 10, 30))  # Corp
            pygame.draw.rect(surface, RED, (self.x, self.y + 5, 10, 3))
            pygame.draw.rect(surface, BLACK, (self.x, self.y + 15, 10, 3))
            pygame.draw.line(surface, SILVER, (self.x + 5, self.y), (self.x + 5, self.y - 10), 2)  # Picior sus
            pygame.draw.line(surface, SILVER, (self.x + 5, self.y + 30), (self.x + 5, self.y + 40), 2)  # Picior jos

        elif self.type == "CAPACITOR":
            # Cilindru albastru
            pygame.draw.circle(surface, BLUE, (self.x + 10, self.y + 10), 10)
            pygame.draw.rect(surface, BLUE, (self.x, self.y + 10, 20, 20))
            pygame.draw.line(surface, SILVER, (self.x + 10, self.y + 30), (self.x + 10, self.y + 40), 2)

        elif self.type == "WATER":
            # Picătură
            pygame.draw.circle(surface, CYAN, (self.x + 10, self.y + 15), 10)
            pygame.draw.polygon(surface, CYAN,
                                [(self.x + 10, self.y), (self.x, self.y + 10), (self.x + 20, self.y + 10)])

        elif self.type == "FIRE":
            # Foc (Roșu/Galben)
            pygame.draw.circle(surface, RED, (self.x + 15, self.y + 15), 15)
            pygame.draw.circle(surface, (255, 165, 0), (self.x + 15, self.y + 15), 8)

        elif self.type == "ESD":
            # Fulger (Galben)
            pts = [(self.x + 10, self.y), (self.x, self.y + 15), (self.x + 10, self.y + 15), (self.x + 5, self.y + 30)]
            pygame.draw.lines(surface, GOLD, False, pts, 3)

    def get_rect(self):
        # Returnează un dreptunghi aproximativ pentru coliziuni
        if self.type == "RAM": return pygame.Rect(self.x, self.y, 60, 20)
        if self.type == "RESISTOR": return pygame.Rect(self.x, self.y - 10, 10, 50)
        return pygame.Rect(self.x, self.y, 40, 40)


# --- JOC PRINCIPAL ---
def main():
    player = Player()
    items = []
    score = 0
    lives = 3

    # Statistici componente
    collected = {"CPU": 0, "FPGA": 0, "RAM": 0}

    game_active = True
    spawn_timer = 0

    running = True
    while running:
        # 1. Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not game_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Restart
                    player = Player()
                    items = []
                    score = 0
                    lives = 3
                    collected = {"CPU": 0, "FPGA": 0, "RAM": 0}
                    game_active = True

        # Mișcare Jucător (Taste sau Mouse)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player.move(-player.speed)
        if keys[pygame.K_RIGHT]: player.move(player.speed)

        # Mouse override
        if pygame.mouse.get_pressed()[0]:
            mx, _ = pygame.mouse.get_pos()
            # Mișcare lină spre mouse
            if mx < player.x + player.width // 2:
                player.move(-player.speed)
            elif mx > player.x + player.width // 2:
                player.move(player.speed)

        # 2. Update
        if game_active:
            # Spawn componente
            spawn_timer += 1
            if spawn_timer > 40:  # Rata de apariție
                items.append(FallingItem())
                spawn_timer = 0

            # Update items
            for item in items[:]:
                item.update()

                # Coliziune
                if player.rect.colliderect(item.get_rect()):
                    if item.is_good:
                        score += 100
                        # Numărăm componentele speciale
                        if item.type in collected: collected[item.type] += 1
                    else:
                        lives -= 1
                        # Feedback vizual scurt (ecran roșu)
                        screen.fill(RED)
                        pygame.display.flip()
                        pygame.time.delay(50)

                    items.remove(item)

                # Ieșire din ecran
                elif item.y > HEIGHT:
                    items.remove(item)
                    # Opțional: Pierzi puncte dacă scapi componente bune?
                    # if item.is_good: score -= 10

            if lives <= 0:
                game_active = False

        # 3. Desenare
        # Fundal PCB
        screen.blit(bg_surface, (0, 0))

        # Jucător
        player.draw(screen)

        # Elemente
        for item in items:
            item.draw(screen)

        # UI (Interfață)
        if game_active:
            # Bară sus
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 50))
            pygame.draw.line(screen, GOLD, (0, 50), (WIDTH, 50), 2)

            # Texte
            txt_score = font_ui.render(f"SCORE: {score}", True, GOLD)
            txt_lives = font_ui.render(f"INTEGRITY: {lives * 33}%", True, RED if lives == 1 else GREEN)

            screen.blit(txt_score, (20, 15))
            screen.blit(txt_lives, (WIDTH - 200, 15))

            # Inventar rapid
            info = f"CPU: {collected['CPU']} | RAM: {collected['RAM']} | FPGA: {collected['FPGA']}"
            txt_inv = font_ui.render(info, True, WHITE)
            screen.blit(txt_inv, (WIDTH // 2 - 150, 15))

        else:
            # Game Over
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200);
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            t1 = font_big.render("SYSTEM FAILURE", True, RED)
            t2 = font_ui.render(f"Final Score: {score}", True, WHITE)
            t3 = font_ui.render(f"Hardware Assembled: {sum(collected.values())} pcs", True, GOLD)
            t4 = font_ui.render("Press 'R' to Reboot System", True, CYAN)

            screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 60))
            screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 + 10))
            screen.blit(t3, (WIDTH // 2 - t3.get_width() // 2, HEIGHT // 2 + 40))
            screen.blit(t4, (WIDTH // 2 - t4.get_width() // 2, HEIGHT // 2 + 90))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()