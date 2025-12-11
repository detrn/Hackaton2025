import sys
import csv
import os
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap

class LeaderboardWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # --- 1. CONFIGURARE CĂI ---
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.ui_path = os.path.join(self.current_dir, "LeaderBoard.ui")
        self.db_path = os.path.join(self.current_dir, "database.csv")
        self.css_path = os.path.join(self.current_dir, "style.qss")

        # --- 2. ÎNCĂRCARE UI ---
        try:
            if os.path.exists(self.ui_path):
                from PyQt6 import uic
                uic.loadUi(self.ui_path, self)
                if hasattr(self, 'pushButton'): self.pushButton.clicked.connect(self.go_back)
                if hasattr(self, 'btnClose'): self.btnClose.clicked.connect(self.go_back)
                if hasattr(self, 'commandLinkButton'): self.commandLinkButton.clicked.connect(self.go_back)
            else:
                self.setup_fallback_ui()
        except Exception as e:
            print(f"Eroare încărcare UI: {e}")
            self.setup_fallback_ui()

        self.setWindowTitle("Clasament General")

        if os.path.exists(self.css_path):
            with open(self.css_path, "r") as f:
                self.setStyleSheet(f.read())

        self.load_data()

    def setup_fallback_ui(self):
        cw = QtWidgets.QWidget()
        self.setCentralWidget(cw)
        layout = QtWidgets.QVBoxLayout(cw)

        lbl = QtWidgets.QLabel("CLASAMENT")
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(lbl)

        self.tableView = QtWidgets.QTableView()
        layout.addWidget(self.tableView)

        self.btnBack = QtWidgets.QPushButton("⬅ Înapoi")
        self.btnBack.setMinimumHeight(50)
        self.btnBack.clicked.connect(self.go_back)
        layout.addWidget(self.btnBack)

        self.resize(900, 600)

    def go_back(self):
        self.close()
        self.go_back_signal.emit()

    def load_data(self):
        players_list = []

        if not os.path.exists(self.db_path):
            print("Baza de date nu există.")
            return

        try:
            with open(self.db_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if "Nume" not in row: continue
                    nume = row["Nume"].strip()
                    raw_avatar = row.get("Avatar", "").strip()
                    spec = row.get("Specializare", "N/A").strip()
                    try:
                        punctaj = int(row.get("Punctaj", 0))
                    except:
                        punctaj = 0

                    players_list.append({
                        "nume": nume,
                        "avatar": raw_avatar,
                        "spec": spec,
                        "punctaj": punctaj
                    })

        except Exception as e:
            print(f"Eroare citire CSV: {e}")

        sorted_players = sorted(players_list, key=lambda x: x['punctaj'], reverse=True)
        self.display_table(sorted_players)

    def display_table(self, data):
        if not hasattr(self, 'tableView'):
            return

        headers = ["Loc", "Avatar", "Nume", "Specializare", "Punctaj"]
        model = QStandardItemModel(len(data), len(headers))
        model.setHorizontalHeaderLabels(headers)

        self.tableView.setIconSize(QtCore.QSize(60, 60))
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.verticalHeader().setDefaultSectionSize(70)
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        for i, info in enumerate(data):
            # 0. Loc
            item_loc = QStandardItem(str(i + 1))
            item_loc.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            model.setItem(i, 0, item_loc)

            # 1. Avatar
            item_avatar = QStandardItem()
            avatar_path = info['avatar']
            possible_paths = [avatar_path, os.path.join(self.current_dir, avatar_path)]
            found_icon = False
            for path in possible_paths:
                if os.path.exists(path):
                    pixmap = QPixmap(path).scaled(60, 60, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
                    item_avatar.setIcon(QIcon(pixmap))
                    found_icon = True
                    break
            if not found_icon:
                item_avatar.setText("No Img")
            model.setItem(i, 1, item_avatar)

            # 2. Nume
            item_nume = QStandardItem(info['nume'])
            item_nume.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
            font_nume = item_nume.font()
            font_nume.setPointSize(12)
            item_nume.setFont(font_nume)
            model.setItem(i, 2, item_nume)

            # 3. Specializare
            item_spec = QStandardItem(info['spec'])
            item_spec.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            font_spec = item_spec.font()
            font_spec.setBold(True)
            item_spec.setFont(font_spec)
            colors = {"AIA": "#2980b9","IE": "#d35400","IEC": "#8e44ad","IETTI": "#16a085"}
            if info['spec'] in colors:
                item_spec.setForeground(QtGui.QColor(colors[info['spec']]))
            model.setItem(i, 3, item_spec)

            # 4. Punctaj
            item_score = QStandardItem(str(info['punctaj']))
            item_score.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            font_score = item_score.font()
            font_score.setBold(True)
            font_score.setPointSize(14)
            item_score.setFont(font_score)
            model.setItem(i, 4, item_score)

        self.tableView.setModel(model)
        self.tableView.setColumnWidth(0, 50)
        self.tableView.setColumnWidth(1, 80)
        self.tableView.setColumnWidth(3, 120)
        self.tableView.setColumnWidth(4, 100)
        self.tableView.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = LeaderboardWindow()
    window.show()
    sys.exit(app.exec())
