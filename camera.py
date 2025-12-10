# camera.py
import cv2
from PyQt5.QtGui import QImage
import numpy as np

class Camera:
    def __init__(self, device_index=0, width=640, height=480):
        self.cap = cv2.VideoCapture(device_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def get_frame(self):
        """
        Returnează frame-ul curent de la cameră ca numpy array BGR
        """
        if not self.cap.isOpened():
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        return frame

    def get_qimage(self):
        """
        Returnează frame-ul curent ca QImage pentru PyQt5.
        Dacă nu există cameră, returnează un frame dummy negru.
        """
        frame = self.get_frame()
        if frame is None:
            # fallback: frame negru
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Convert BGR -> RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qimage = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return qimage

    def release(self):
        """
        Eliberează resursele camerei
        """
        if self.cap.isOpened():
            self.cap.release()
