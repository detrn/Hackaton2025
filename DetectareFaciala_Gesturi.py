import cv2
import pygame
import requests
import io
import random
import os
import sys

# ==========================================
# PARTEA 1: OPENCV - DETECȚIE ZÂMBET
# ==========================================

cascade_face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cascade_smile = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

if cascade_face.empty() or cascade_smile.empty():
    print("Eroare: Nu s-au putut încărca fișierele XML haarcascade!")
    sys.exit()


def get_face_coordinates(frame_gray):
    faces = cascade_face.detectMultiScale(frame_gray, 1.2, 5, minSize=(60, 60))
    if len(faces) > 0:
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        return faces[0]
    return None


def detecteaza_zambet_in_roi(roi_gray):
    smiles = cascade_smile.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=25, minSize=(25, 25))
    return len(smiles) > 0


def asteapta_zambetul_utilizatorului():
    print("Se deschide camera... Zâmbește pentru a debloca aplicația.")
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Eroare: Camera nu s-a putut deschide!")
        return False

    consecutive_smile_frames = 0
    SMILE_THRESHOLD = 5

    while True:
        ret, frame = cam.read()
        if not ret: break

        frame = cv2.flip(frame, 1)
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_coords = get_face_coordinates(frame_gray)

        status_text = "Priveste la camera..."
        color = (0, 0, 255)

        if face_coords is not None:
            (x, y, w, h) = face_coords
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            roi_gray = frame_gray[y:y + h, x:x + w]
            is_smiling = detecteaza_zambet_in_roi(roi_gray)

            if is_smiling:
                consecutive_smile_frames += 1
                status_text = f"Zambet detectat! Mentine... {consecutive_smile_frames}/{SMILE_THRESHOLD}"
                color = (0, 255, 255)
            else:
                consecutive_smile_frames = max(0, consecutive_smile_frames - 1)
                status_text = "Fata detectata. Zambeste!"
                color = (255, 0, 0)

            if consecutive_smile_frames >= SMILE_THRESHOLD:
                print("Zâmbet confirmat! Pornim aplicația...")
                status_text = "Succes! Pornire..."
                color = (0, 255, 0)
                cv2.putText(frame, status_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                cv2.imshow('Detectie Zambet', frame)
                cv2.waitKey(500)
                cam.release()
                cv2.destroyAllWindows()
                return True

        cv2.putText(frame, status_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.imshow('Detectie Zambet', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cam.release()
            cv2.destroyAllWindows()
            return False


# ==========================================
# PARTEA 2: PYGAME - GENERATOR & SAVE
# ==========================================

WIDTH, HEIGHT = 1000, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BTN_BLUE = (70, 130, 180)
BTN_GREEN = (40, 180, 100)  # Culoare pentru butonul de Save


def crop_circle(surface):
    size = surface.get_size()
    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (size[0] // 2, size[1] // 2), size[0] // 2)
    new_surf = surface.copy().convert_alpha()
    new_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return new_surf


def genereaza_avatar_online():
    seed = random.randint(1, 999999)
    stil = "avataaars"
    url = f"https://api.dicebear.com/9.x/{stil}/png?seed={seed}&backgroundColor=transparent"
    print(f"Generez avatar de la: {url}")
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        image_stream = io.BytesIO(response.content)
        avatar = pygame.image.load(image_stream).convert_alpha()
        avatar = pygame.transform.smoothscale(avatar, (400, 400))
        avatar = crop_circle(avatar)
        return avatar
    except Exception as e:
        print(f"Eroare: {e}")
        fallback = pygame.Surface((400, 400))
        fallback.fill((255, 0, 0))
        return fallback


def run_pygame_app():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("IETTI: Online Avatar Generator")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 30)
    font_small = pygame.font.SysFont("Arial", 20)

    # Ecran Loading
    screen.fill(WHITE)
    msg = font.render("Zâmbet confirmat! Se descarcă avatarul...", True, BLACK)
    screen.blit(msg, (WIDTH // 2 - 250, HEIGHT // 2))
    pygame.display.flip()

    # Generare inițială
    avatar_big = genereaza_avatar_online()
    avatar_mini = pygame.transform.smoothscale(avatar_big, (120, 120))

    pos_mini = (20, 20)
    rect_mini = pygame.Rect(pos_mini[0], pos_mini[1], 120, 120)
    pos_big = (WIDTH // 2 - 200, HEIGHT // 2 - 200)

    # --- BUTOANE ---
    # Buton Regenerare (Dreapta jos)
    regen_btn = pygame.Rect(WIDTH - 220, HEIGHT - 100, 200, 60)
    # Buton Salvare (Stânga jos față de cel de regenerare)
    save_btn = pygame.Rect(WIDTH - 440, HEIGHT - 100, 200, 60)

    state = 'MAIN_APP'
    saved_message_timer = 0  # Pentru a afișa "Salvat!" timp de 2 secunde

    running = True
    while running:
        screen.fill(WHITE)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if state == 'MAIN_APP':
                    if rect_mini.collidepoint(mx, my): state = 'VIEWER'

                    # 1. LOGICĂ REGENERARE
                    if regen_btn.collidepoint(mx, my):
                        # Desenăm loading rapid
                        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 200, HEIGHT // 2, 400, 50))
                        load_txt = font.render("Se descarcă...", True, BLACK)
                        screen.blit(load_txt, (WIDTH // 2 - 100, HEIGHT // 2))
                        pygame.display.flip()

                        avatar_big = genereaza_avatar_online()
                        avatar_mini = pygame.transform.smoothscale(avatar_big, (120, 120))
                        saved_message_timer = 0  # Resetăm mesajul de salvare

                    # 2. LOGICĂ SALVARE
                    if save_btn.collidepoint(mx, my):
                        # Salvăm avatarul mare
                        nume_fisier = "avatar_downloaded.png"
                        pygame.image.save(avatar_big, nume_fisier)
                        print(f"Imagine salvată ca {nume_fisier}")
                        saved_message_timer = 120  # Afișăm mesajul timp de 120 frame-uri (2 sec)

                elif state == 'VIEWER':
                    state = 'MAIN_APP'

        if state == 'MAIN_APP':
            # Background
            for i in range(0, HEIGHT, 20): pygame.draw.line(screen, (240, 240, 255), (0, i), (WIDTH, i))
            pygame.draw.circle(screen, (200, 200, 200), (pos_mini[0] + 60, pos_mini[1] + 60), 62)
            screen.blit(avatar_mini, pos_mini)

            welcome = font.render("Aplicație Profil Online", True, BLACK)
            screen.blit(welcome, (WIDTH // 2 - 120, HEIGHT // 2))

            # --- DESENARE BUTOANE ---

            # Buton Regenerare (Albastru)
            pygame.draw.rect(screen, BTN_BLUE, regen_btn, border_radius=10)
            btn_txt = font.render("Alt Avatar", True, WHITE)
            screen.blit(btn_txt, (regen_btn.x + 40, regen_btn.y + 15))

            # Buton Salvare (Verde)
            pygame.draw.rect(screen, BTN_GREEN, save_btn, border_radius=10)
            save_txt = font.render("Salvează", True, WHITE)
            screen.blit(save_txt, (save_btn.x + 45, save_btn.y + 15))

            # --- MESAJ CONFIRMARE SALVARE ---
            if saved_message_timer > 0:
                saved_message_timer -= 1
                msg_saved = font_small.render("Imagine salvată cu succes!", True, BTN_GREEN)
                screen.blit(msg_saved, (save_btn.x, save_btn.y - 30))

        elif state == 'VIEWER':
            s = pygame.Surface((WIDTH, HEIGHT));
            s.set_alpha(220);
            s.fill(BLACK);
            screen.blit(s, (0, 0))
            screen.blit(avatar_big, pos_big)
            pygame.draw.circle(screen, WHITE, (WIDTH // 2, HEIGHT // 2), 200, 5)
            info = font.render("Click oriunde pentru a închide", True, WHITE)
            screen.blit(info, (WIDTH // 2 - 180, HEIGHT - 100))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    if asteapta_zambetul_utilizatorului():
        run_pygame_app()
    else:
        print("Ieșire.")