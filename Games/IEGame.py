import pygame, random, time, sys, os, csv, subprocess

# --- CONFIGURARE ---
if len(sys.argv) > 4:
    PLAYER_NAME, PLAYER_AVATAR, PLAYER_SPEC, PLAYER_ID = sys.argv[1:5]
else:
    PLAYER_NAME, PLAYER_AVATAR, PLAYER_SPEC, PLAYER_ID = "Test", "path", "IE", "000"


def save_score_csv(nume, avatar, specializare, punctaj):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.csv")
    try:
        exist = os.path.isfile(path)
        with open(path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Nume", "Avatar", "Specializare", "Punctaj"])
            if not exist: writer.writeheader()
            writer.writerow({"Nume": nume, "Avatar": avatar, "Specializare": specializare, "Punctaj": punctaj})
    except:
        pass


class IEGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 500))
        pygame.display.set_caption(f"IE ({PLAYER_SPEC}) - {PLAYER_NAME}")
        self.FONT = pygame.font.Font(None, 50)
        self.SMALL = pygame.font.Font(None, 30)
        self.next_action = None

        self.COLORS = [(255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 0), (0, 255, 255),
                       (255, 165, 0)]
        self.Y_POS = [100, 160, 220, 280, 340, 400, 460]
        self.TARGETS = [{"c": c, "r": pygame.Rect(600, y - 30, 100, 60)} for c, y in zip(self.COLORS, self.Y_POS)]

        self.reset()

    def reset(self):
        random.shuffle(self.Y_POS)
        self.wires = [{"c": c, "s": [150, y], "ok": False} for c, y in zip(self.COLORS, self.Y_POS)]
        self.drag = None
        self.start_time = time.time()
        self.mistakes = 0
        self.finished = False
        self.score_saved = False

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            self.screen.fill((30, 30, 30))
            elapsed = time.time() - self.start_time
            time_left = max(0, 60 - elapsed)

            # --- CALCUL SCOR ---
            # 5000 - (Timp * 50) - (Greseli * 200)
            score = int(5000 - (elapsed * 50) - (self.mistakes * 200))
            score = max(0, score)

            if time_left <= 0: self.finished = True
            if all(w["ok"] for w in self.wires): self.finished = True

            # --- EVENIMENTE ---
            for e in pygame.event.get():
                if e.type == pygame.QUIT: running = False

                if not self.finished:
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = pygame.mouse.get_pos()
                        for w in self.wires:
                            if not w["ok"] and abs(mx - w["s"][0]) < 20 and abs(my - w["s"][1]) < 20:
                                self.drag = w
                    elif e.type == pygame.MOUSEBUTTONUP:
                        if self.drag:
                            mx, my = pygame.mouse.get_pos()
                            hit = False
                            for t in self.TARGETS:
                                if t["r"].collidepoint(mx, my):
                                    if t["c"] == self.drag["c"]:
                                        self.drag["s"] = list(t["r"].center)
                                        self.drag["ok"] = True
                                        hit = True
                                    else:
                                        # GREEALĂ!
                                        self.mistakes += 1
                            self.drag = None
                else:
                    # Final joc - Buton
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = pygame.mouse.get_pos()
                        if 250 < mx < 550 and 350 < my < 410:
                            self.next_action = "leaderboard"
                            running = False

            # --- DESENARE ---
            self.screen.blit(self.FONT.render(f"TIMP: {int(time_left)}", True, (255, 255, 255)), (20, 20))
            self.screen.blit(self.FONT.render(f"SCOR: {score}", True, (255, 255, 255)), (550, 20))

            for t in self.TARGETS:
                pygame.draw.rect(self.screen, t["c"], t["r"])
                self.screen.blit(self.SMALL.render("Circuit", True, (0, 0, 0)), (t["r"].x + 10, t["r"].y + 20))

            for w in self.wires:
                pygame.draw.circle(self.screen, w["c"], w["s"], 15)
                if w == self.drag:
                    mx, my = pygame.mouse.get_pos()
                    pygame.draw.line(self.screen, w["c"], w["s"], (mx, my), 5)
                elif w["ok"]:
                    tgt = next(t["r"] for t in self.TARGETS if t["c"] == w["c"])
                    pygame.draw.line(self.screen, w["c"], w["s"], tgt.center, 5)

            if self.finished:
                if not self.score_saved:
                    save_score_csv(PLAYER_NAME, PLAYER_AVATAR, PLAYER_SPEC, score)
                    self.score_saved = True

                s = pygame.Surface((800, 500))
                s.set_alpha(200);
                s.fill((0, 0, 0))
                self.screen.blit(s, (0, 0))

                txt = "TIMP EXPIRAT!" if time_left <= 0 else "CIRCUIT COMPLET!"
                col = (255, 50, 50) if time_left <= 0 else (0, 255, 0)
                self.screen.blit(self.FONT.render(txt, True, col), (250, 200))
                self.screen.blit(self.SMALL.render(f"Scor Final: {score}", True, (255, 255, 255)), (330, 280))

                pygame.draw.rect(self.screen, (100, 100, 100), (250, 350, 300, 60), border_radius=10)
                self.screen.blit(self.FONT.render("Leaderboard", True, (255, 255, 255)), (280, 360))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        if self.next_action == "leaderboard":
            try:
                subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "Leaderboard.py")])
            except:
                pass
        sys.exit()


if __name__ == "__main__":
    IEGame().run()