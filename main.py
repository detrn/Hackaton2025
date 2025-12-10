import sys
import cv2
from PyQt5.QtWidgets import QApplication

# Aici importăm clasele tale din celelalte fișiere
from avatar_generator import AvatarGenerator
from camera import Camera


def main():
    # 1. Inițializare QApplication (Obligatoriu pentru PyQt5)
    app = QApplication(sys.argv)

    print("--- TESTARE AVATAR ---")
    # Generăm un avatar
    pixmap = AvatarGenerator.generate(seed="Utilizator123")

    if pixmap:
        print("Avatar generat cu succes! (Obiect QPixmap creat)")
        # Aici l-ai pune într-un QLabel: label.setPixmap(pixmap)
    else:
        print("Eroare la generarea avatarului.")

    print("\n--- TESTARE CAMERA ---")
    print("Apasă 'q' pentru a ieși.")

    # Inițializăm camera
    cam = Camera()

    while True:
        # Luăm un cadru
        frame = cam.get_frame()

        if frame is not None:
            # Detectăm zâmbetul
            zambeste, frame_procesat = cam.detect_smile(frame)

            if zambeste:
                cv2.putText(frame_procesat, "ZAMBESTE! :)", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Afișăm fereastra (folosind OpenCV pentru simplitate aici)
            cv2.imshow('Camera Feed', frame_procesat)

        # Ieșire cu tasta 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Curățăm resursele
    cam.release()
    cv2.destroyAllWindows()
    sys.exit()


if __name__ == "__main__":
    main()