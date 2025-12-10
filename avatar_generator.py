import random
import requests
import os  # <--- 1. Importam os (optional, dar bun pentru verificari)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QBrush
from PyQt5.QtCore import Qt


class AvatarGenerator:
    @staticmethod
    def generate(seed=None):
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
            image = image.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # Creăm imaginea rotundă
            out_img = QImage(size, size, QImage.Format_ARGB32)
            out_img.fill(Qt.transparent)

            brush = QBrush(image)
            painter = QPainter(out_img)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(brush)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, size, size)
            painter.end()

            # =================================================
            # PARTEA DE SALVARE ÎN FIȘIER
            # =================================================
            nume_fisier = "avatar_student.png"

            # Salvăm imaginea procesată (rotundă) pe disc
            succes = out_img.save(nume_fisier, "PNG")

            if succes:
                print(f"✅ Avatar salvat cu succes: {nume_fisier}")
            else:
                print("❌ Eroare la salvarea avatarului pe disc.")
            # =================================================

            return QPixmap.fromImage(out_img)

        except Exception as e:
            print(f"Eroare retea sau procesare avatar: {e}")
            return None