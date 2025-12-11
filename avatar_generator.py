import datetime
import random
import requests
import os
from PyQt6.QtGui import QImage, QPixmap, QPainter, QBrush
from PyQt6.QtCore import Qt


class AvatarGenerator:
    @staticmethod
    def generate(seed=None):
        # Asigurăm existența folderului 'asset'
        if not os.path.exists("asset"):
            os.makedirs("asset")

        if seed is None:
            seed = random.randint(1, 999999)

        stil = "pixel-art"
        url = f"https://api.dicebear.com/9.x/{stil}/png?seed={seed}&backgroundColor=transparent"

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            image = QImage()
            image.loadFromData(response.content)

            size = 400
            # În PyQt6, parametrii sunt la fel, doar că KeepAspectRatio e din QtCore.Qt
            image = image.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            # Creăm imaginea rotundă
            out_img = QImage(size, size, QImage.Format.Format_ARGB32)
            out_img.fill(Qt.GlobalColor.transparent)

            brush = QBrush(image)
            painter = QPainter(out_img)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(brush)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(0, 0, size, size)
            painter.end()

            # --- SALVARE ---
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nume_fisier = f"asset/avatar_student_{timestamp}.png"

            out_img.save(nume_fisier, "PNG")

            # Returnăm tuple: (QPixmap, calea_fisierului)
            return QPixmap.fromImage(out_img), nume_fisier

        except Exception as e:
            print(f"Eroare avatar: {e}")
            return None, None
