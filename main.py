# main.py
import sys
from PyQt5.QtWidgets import QApplication
from GUI.fereastraPrincipala import MainWindow  # presupunem că MainWindow e definit aici


def main():
    # Creează aplicația PyQt
    app = QApplication(sys.argv)

    # Creează și arată fereastra principală
    window = MainWindow()
    window.showMaximized()  # sau window.show() pentru fereastră normală

    # Rulează aplicația
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
