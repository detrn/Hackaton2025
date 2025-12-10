import cv2


class Camera:
    def __init__(self):
        # Inițializăm camera (index 0 de obicei e camera web default)
        self.cap = cv2.VideoCapture(0)

        # Încărcăm clasificatorii pentru față și zâmbet
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

    def get_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Oglindim imaginea (flip orizontal) pentru a părea oglindă
                return cv2.flip(frame, 1)
        return None

    def detect_smile(self, frame):
        # Convertim la alb-negru pentru detecție (e mai rapid)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectăm fețele
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(60, 60))
        is_smiling = False

        for (x, y, w, h) in faces:
            # Desenăm dreptunghi pe față (albastru)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Zona de interes (doar fața) pentru a căuta zâmbetul
            roi_gray = gray[y:y + h, x:x + w]

            # Parametrii scaleFactor și minNeighbors sunt ajustați pentru a reduce alarmele false
            smiles = self.smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=25, minSize=(25, 25))

            if len(smiles) > 0:
                is_smiling = True
                for (sx, sy, sw, sh) in smiles:
                    # Desenăm dreptunghi pe zâmbet (verde)
                    cv2.rectangle(frame, (x + sx, y + sy), (x + sx + sw, y + sy + sh), (0, 255, 0), 1)

        return is_smiling, frame

    def release(self):
        if self.cap.isOpened():
            self.cap.release()