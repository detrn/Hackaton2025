
import cv2

try:
    cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    smile_cascade = cv2.CascadeClassifier('haarcascade_smile.xml')
    if cascade.empty() or smile_cascade.empty():
        raise IOError('Cascade not found')
except IOError as error:
    print("Eroare la deschidere fisierului 'cascade'!!!!")
    cascade = None

#functie cara returneaza coordonatele primei fete pe care o gaseste
def get_face_coordinates(frame):
    if cascade is None:
        return None
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(frame_gray, 1.2, 5,50)
    if len(faces) > 0:
        return faces[0]
    else:
        return None
def zambet(roi_gray):
    if smile_cascade is None:
        return False
    smiles = smile_cascade.detectMultiScale(roi_gray,scaleFactor=1.7, minNeighbors=20, minSize=(25, 25), flags=cv2.CASCADE_SCALE_IMAGE)
    return len(smiles) > 0
def recunoastereFacialaSiZambet():
    CAMERA_INDEX = 0
    cam = cv2.VideoCapture(CAMERA_INDEX)

    if not cam.isOpened():
        print("Camera nu s a putut deschide!")
        exit()

    while True:
        ret, frame = cam.read()
        if not ret:
            break
        rezultat = get_face_coordinates(frame)
        zambet_detectat=False
        if rezultat is not None:
            (x, y, w, h) = rezultat
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_color=frame[y:y + h, x:x + w]
            roi_gray= cv2.cvtColor(roi_color, cv2.COLOR_BGR2GRAY)
            zambet_detectat=zambet(roi_gray)
        if(zambet_detectat):
            cv2.imwrite("fata_zambareata.jpg",frame)
        cv2.imshow('frame',frame)
        cv2.imshow("Test Detectie Fata", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
recunoastereFacialaSiZambet()
