import sys
import csv
import os
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon


class LeaderboardWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ui_path = os.path.join(base_dir, "LeaderBoard.ui")
        self.db_path = os.path.join(base_dir, "database.csv")
        self.css_path = os.path.join(base_dir, "style.qss")

        try:
            if os.path.exists(self.ui_path):
                uic.loadUi(self.ui_path, self)
            else:
                self.tableView = QtWidgets.QTableView()
                self.setCentralWidget(self.tableView)
                self.resize(600, 500)
                print(f"EROARE: Nu găsesc {self.ui_path}")
        except Exception as e:
            print(f"Eroare UI: {e}")

        self.setWindowTitle("Clasament General")


        if hasattr(self, 'pushButton'):
            self.pushButton.clicked.connect(self.close)

        if hasattr(self, 'commandLinkButton'):
            self.commandLinkButton.clicked.connect(self.close)
        elif hasattr(self, 'btnClose'):
            self.btnClose.clicked.connect(self.close)

        self.load_stylesheet()
        self.load_data()

    def load_data(self):
        players_map = {}

        if not os.path.exists(self.db_path):
            QtWidgets.QMessageBox.warning(self, "Eroare", "Nu găsesc database.csv")
            return

        try:
            with open(self.db_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    # Curățăm datele de spații
                    row = {k.strip(): v for k, v in row.items() if k}

                    if "Nume" not in row: continue

                    nume = row["Nume"]

                    raw_avatar = row.get("Avatar", "").strip()
                    if raw_avatar and not os.path.isabs(raw_avatar):
                        avatar_full_path = os.path.join(os.path.dirname(self.db_path), raw_avatar)
                    else:
                        avatar_full_path = raw_avatar

                    try:
                        punctaj = int(row.get("Punctaj", 0))
                    except ValueError:
                        punctaj = 0

                    if nume in players_map:
                        if punctaj > players_map[nume]["punctaj"]:
                            players_map[nume] = {"avatar": avatar_full_path, "punctaj": punctaj}
                    else:
                        players_map[nume] = {"avatar": avatar_full_path, "punctaj": punctaj}

        except Exception as e:
            print(f"Eroare citire CSV: {e}")
            return

        sorted_players = sorted(
            players_map.items(),
            key=lambda item: item[1]['punctaj'],
            reverse=True
        )

        self.display_in_table(sorted_players)

    def display_in_table(self, top_list):
        if not hasattr(self, 'tableView'): return

        headers = ["Loc", "Avatar", "Nume", "Punctaj"]
        model = QStandardItemModel(len(top_list), len(headers))
        model.setHorizontalHeaderLabels(headers)
        self.tableView.setIconSize(QtCore.QSize(40, 40))

        for i, (nume, data) in enumerate(top_list):
            # Loc
            item_rank = QStandardItem(str(i + 1))
            item_rank.setTextAlignment(QtCore.Qt.AlignCenter)
            model.setItem(i, 0, item_rank)

            # Avatar
            item_avatar = QStandardItem()
            if os.path.exists(data["avatar"]):
                item_avatar.setIcon(QIcon(data["avatar"]))
            else:
                item_avatar.setText("No Img")
            model.setItem(i, 1, item_avatar)

            model.setItem(i, 2, QStandardItem(nume))

            item_score = QStandardItem(str(data["punctaj"]))
            item_score.setTextAlignment(QtCore.Qt.AlignCenter)
            font = item_score.font();
            font.setBold(True)
            item_score.setFont(font)
            model.setItem(i, 3, item_score)

        self.tableView.setModel(model)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.setColumnWidth(1, 60)
        self.tableView.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

    def load_stylesheet(self):
        if os.path.exists(self.css_path):
            with open(self.css_path, "r") as f:
                self.setStyleSheet(f.read())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = LeaderboardWindow()
    window.show()
    sys.exit(app.exec_())