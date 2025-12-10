'''
# =======================================================================
# EXEMPLU DE COD AVATAR (NU RULEAZA - ESTE DOAR PENTRU REFERINTA)
# =======================================================================

import pygame
import requests
import io
import random

# ==========================================
# SETĂRI GRAFICE
# ==========================================
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BTN_BLUE = (70, 130, 180)   # Culoare Regenerare
BTN_GREEN = (40, 180, 100)  # Culoare Salvare
BG_COLOR = (240, 240, 255)  # Fundal

# ==========================================
# FUNCȚII GENERARE & PRELUCRARE
# ==========================================

def crop_circle(surface):
    """ Taie imaginea sub formă de cerc """
    size = surface.get_size()
    # Creăm o mască (cerc alb)
    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (size[0] // 2, size[1] // 2), size[0] // 2)

    # Copiem imaginea și aplicăm masca
    new_surf = surface.copy().convert_alpha()
    new_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return new_surf

def genereaza_avatar_online():
    """ Descarcă avatarul de la DiceBear """
    seed = random.randint(1, 999999)
    # Poți schimba stilul aici: "pixel-art", "adventurer", "avataaars"
    stil = "avataaars"
    url = f"https://api.dicebear.com/9.x/{stil}/png?seed={seed}&backgroundColor=transparent"

    print(f"Generez avatar nou... Seed: {seed}")

    try:
        # Request către API
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        # Încărcare imagine din memorie (bytes) direct în Pygame
        image_stream = io.BytesIO(response.content)
        avatar = pygame.image.load(image_stream).convert_alpha()

        # Redimensionare la 300x300 și tăiere cerc
        avatar = pygame.transform.smoothscale(avatar, (300, 300))
        avatar = crop_circle(avatar)
        return avatar

    except Exception as e:
        print(f"Eroare conexiune: {e}")
        # Returnează un pătrat roșu în caz de eroare
        fallback = pygame.Surface((300, 300))
        fallback.fill((200, 50, 50))
        return fallback

# ==========================================
# INTERFAȚA GRAFICĂ (MAIN)
# ==========================================

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Generator Avatar")
    clock = pygame.time.Clock()

    # Fonturi
    font = pygame.font.SysFont("Arial", 30)
    font_small = pygame.font.SysFont("Arial", 20)

    # -- 1. GENERARE INIȚIALĂ --
    current_avatar = genereaza_avatar_online()

    # Poziționare Avatar (Centrat)
    avatar_rect = current_avatar.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))

    # -- 2. DEFINIRE BUTOANE --
    # Buton Regenerare
    btn_regen = pygame.Rect(0, 0, 200, 50)
    btn_regen.center = (WIDTH // 2 - 110, HEIGHT - 100)

    # Buton Salvare
    btn_save = pygame.Rect(0, 0, 200, 50)
    btn_save.center = (WIDTH // 2 + 110, HEIGHT - 100)

    msg_timer = 0 # Timer pentru mesajul "Salvat!"

    running = True
    while running:
        # --- EVENIMENTE ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                # Click pe REGENERARE
                if btn_regen.collidepoint(mx, my):
                    # Afișăm un text scurt de loading
                    draw_loading(screen, font)
                    current_avatar = genereaza_avatar_online()
                    msg_timer = 0 # Resetăm mesajul de salvare

                # Click pe SALVARE
                if btn_save.collidepoint(mx, my):
                    nume_fisier = f"avatar_{random.randint(1000,9999)}.png"
                    pygame.image.save(current_avatar, nume_fisier)
                    print(f"Salvata ca: {nume_fisier}")
                    msg_timer = 120 # Afișăm mesajul timp de 2 secunde (60fps * 2)

        # --- DESENARE ---
        screen.fill(BG_COLOR)

        # 1. Desenăm Avatarul
        # Facem un cerc gri în spate ca ramă
        pygame.draw.circle(screen, (200, 200, 200), avatar_rect.center, 155)
        screen.blit(current_avatar, avatar_rect)

        # 2. Desenăm Titlul
        title = font.render("Generator Avatar Student", True, BLACK)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 50)))

        # 3. Desenăm Butoanele
        draw_button(screen, btn_regen, BTN_BLUE, "Alt Avatar", font_small)
        draw_button(screen, btn_save, BTN_GREEN, "Salvează PNG", font_small)

        # 4. Mesaj Confirmare Salvare
        if msg_timer > 0:
            msg_timer -= 1
            txt = font_small.render("Imagine Salvată!", True, (0, 150, 0))
            screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT - 40)))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

# Funcții ajutătoare pentru desenare ca să fie codul mai curat
def draw_button(surface, rect, color, text, font):
    pygame.draw.rect(surface, color, rect, border_radius=10)
    # Efect de umbră simplu
    pygame.draw.rect(surface, BLACK, rect, width=2, border_radius=10)

    txt_surf = font.render(text, True, WHITE)
    txt_rect = txt_surf.get_rect(center=rect.center)
    surface.blit(txt_surf, txt_rect)

def draw_loading(surface, font):
    """ Afișează un text simplu în timp ce descarcă """
    rect = pygame.Rect(0, 0, 200, 50)
    rect.center = (WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(surface, WHITE, rect)
    txt = font.render("Se descarcă...", True, BLACK)
    surface.blit(txt, txt.get_rect(center=rect.center))
    pygame.display.flip()

if __name__ == "__main__":
    main()
'''

'''
# =======================================================================
# EXEMPLU TESTARE CAMERA (COD DE REFERINȚĂ - NU RULEAZĂ AUTOMAT)
# =======================================================================
# Acest cod demonstrează cum funcționează detectarea zâmbetului folosind
# doar OpenCV, fără interfața complexă din PyQt5.
# =======================================================================

import cv2
import sys

# ==========================================
# CLASA BACKEND - CAMERA
# ==========================================
class CameraTest:
    def __init__(self):
        # 1. Inițializăm camera (Index 0 = Webcam laptop)
        self.cap = cv2.VideoCapture(0)

        # 2. Încărcăm fișierele "haarcascade" pentru inteligența artificială
        # Acestea sunt pre-instalate cu opencv-python
        path_face = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        path_smile = cv2.data.haarcascades + 'haarcascade_smile.xml'

        self.face_cascade = cv2.CascadeClassifier(path_face)
        self.smile_cascade = cv2.CascadeClassifier(path_smile)

        # Verificăm dacă s-au încărcat corect
        if self.face_cascade.empty() or self.smile_cascade.empty():
            print("EROARE: Nu am putut încărca fișierele XML pentru detecție!")

    def get_frame(self):
        """ Citește un cadru de la cameră și îl oglindește """
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Flip 1 înseamnă oglindire orizontală (ca în oglindă)
                return cv2.flip(frame, 1)
        return None

    def detect_smile_logic(self, frame):
        """ 
        Detectează fața și apoi zâmbetul în interiorul feței.
        Returnează: (True/False, imaginea_desenată)
        """
        # Convertim la gri pentru viteză
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectăm fețele (scaleFactor=1.3, minNeighbors=5)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(60, 60))

        is_smiling = False

        for (x, y, w, h) in faces:
            # Desenăm pătrat albastru pe față
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Decupăm zona feței (Region of Interest - ROI)
            # Căutăm zâmbetul DOAR aici, nu în toată poza
            roi_gray = gray[y:y + h, x:x + w]

            # Detectăm zâmbetul (Setări stricte: scale=1.8, neighbors=25)
            smiles = self.smile_cascade.detectMultiScale(roi_gray, 1.8, 25, minSize=(25, 25))

            if len(smiles) > 0:
                is_smiling = True
                for (sx, sy, sw, sh) in smiles:
                    # Desenăm pătrat verde pe gură (coordonate relative la față)
                    cv2.rectangle(frame, (x + sx, y + sy), (x + sx + sw, y + sy + sh), (0, 255, 0), 1)

        return is_smiling, frame

    def release(self):
        """ Eliberează camera la final """
        if self.cap.isOpened():
            self.cap.release()

# ==========================================
# MAIN - TESTARE FUNCTIONALITATE
# ==========================================
def main_camera_test():
    print("--- PORNIRE TEST CAMERA ---")
    print("Apasă tasta 'q' pentru a ieși.")

    # Inițializăm obiectul cameră
    cam = CameraTest()

    # Variabilă pentru a număra cât timp zâmbești
    smile_counter = 0
    TARGET = 20  # Trebuie să zâmbești 20 de frame-uri

    while True:
        # 1. Luăm imaginea
        frame = cam.get_frame()

        if frame is not None:
            # 2. Procesăm imaginea
            zambeste, frame_procesat = cam.detect_smile_logic(frame)

            # 3. Logica de testare
            if zambeste:
                smile_counter += 1
                color = (0, 255, 0) # Verde
                text = f"ZAMBESTE! {smile_counter}/{TARGET}"
            else:
                smile_counter = max(0, smile_counter - 1)
                color = (0, 0, 255) # Roșu
                text = "Te rog zambeste..."

            # 4. Desenăm textul pe ecran
            cv2.putText(frame_procesat, text, (30, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            # 5. Afișăm fereastra (folosind OpenCV, nu PyQt)
            cv2.imshow('Test Camera Feed', frame_procesat)

            # Dacă am atins ținta
            if smile_counter >= TARGET:
                print("SUCCES! Zâmbet confirmat.")
                smile_counter = 0 # Resetăm pentru test

        # 6. Ieșire cu tasta 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Curățenie la final
    cam.release()
    cv2.destroyAllWindows()
    print("Test finalizat.")

if __name__ == "__main__":
    main_camera_test()
'''