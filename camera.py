import cv2


class Camera:
    def __init__(self):
        # Index 0 este de obicei camera web implicită
        self.cap = cv2.VideoCapture(0)

        # Încărcăm clasificatorii (modelele pre-antrenate pentru față și zâmbet)
        # Acestea vin standard cu OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

    def get_frame(self):
        """Capturează un cadru și îl oglindește."""
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Oglindim imaginea (flip orizontal)
                return cv2.flip(frame, 1)
        return None

    def detect_smile(self, frame):
        """Detectează fața și zâmbetul în cadrul dat."""
        # Convertim la alb-negru pentru procesare (mai rapid)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectăm fețele
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        is_smiling = False

        for (x, y, w, h) in faces:
            # Desenăm un dreptunghi albastru în jurul feței
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Definim zona de interes (doar fața) - căutăm zâmbetul DOAR în interiorul feței
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]

            # Detectăm zâmbetul
            # scaleFactor=1.8 și minNeighbors=20 sunt setări stricte ca să nu detecteze orice gură deschisă ca zâmbet
            smiles = self.smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=20)

            for (sx, sy, sw, sh) in smiles:
                # Dacă am găsit un zâmbet
                is_smiling = True
                # Desenăm dreptunghi verde în jurul gurii
                cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (0, 255, 0), 2)

        return is_smiling, frame

    def release(self):
        """Eliberează resursele camerei."""
        if self.cap.isOpened():
            self.cap.release()