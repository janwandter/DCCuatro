import sys
import os
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QCoreApplication
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QPixmap


class WaitingRoom(QWidget):

    def __init__(self):
        super().__init__()
        self.players = dict()

    def init_gui(self):
        self.setWindowTitle("Waiting Room DDCuatro")
        self.setGeometry(650, 200, 480, 720)

        self.background = QLabel(self)
        path = os.path.join("sprites", "login.png")
        pixeles_back = QPixmap(path)
        self.background.setPixmap(pixeles_back)
        self.background.resize(480, 720)
        self.background.setScaledContents(True)

        self.players_waiting = QLabel("Jugadores conectados", self)
        self.players_waiting.setStyleSheet("background-color: rgba(1,1,1,0); color: white")
        self.players_waiting.setFont(QFont("SansSerif", 12))
        self.players_waiting.resize(480, 30)
        self.players_waiting.move(0, 425)
        self.players_waiting.setAlignment(Qt.AlignCenter)

        self.player_1 = QLabel("Waiting..", self)
        self.player_1.setStyleSheet("background-color: rgba(1,1,1,0); color: grey")
        self.player_1.setFont(QFont("SansSerif", 12))
        self.player_1.move(100, 500)
        self.player_1.resize(170, 30)
        self.players["1"] = self.player_1

        self.player_2 = QLabel("Waiting..", self)
        self.player_2.setStyleSheet("background-color: rgba(1,1,1,0); color: grey")
        self.player_2.setFont(QFont("SansSerif", 12))
        self.player_2.move(100, 600)
        self.player_2.resize(170, 30)
        self.players["2"] = self.player_2

        self.player_3 = QLabel("Waiting..", self)
        self.player_3.setStyleSheet("background-color: rgba(1,1,1,0); color: grey")
        self.player_3.setFont(QFont("SansSerif", 12))
        self.player_3.move(300, 500)
        self.player_3.resize(170, 30)
        self.players["3"] = self.player_3

        self.player_4 = QLabel("Waiting..", self)
        self.player_4.setStyleSheet("background-color: rgba(1,1,1,0); color: grey")
        self.player_4.setFont(QFont("SansSerif", 12))
        self.player_4.move(300, 600)
        self.player_4.resize(170, 30)
        self.players["4"] = self.player_4

        self.show()

    def update_players(self, data):
        for username in data:
            self.players[data[username]].setText(f"{username}")
            self.players[data[username]].setStyleSheet("color: white")
        for waiting in range(1, 4 + 1):
            if f"{waiting}" not in data.values():
                self.players[f"{waiting}"].setText(f"Waiting..")
                self.players[f"{waiting}"].setStyleSheet("color: grey")

    def close(self):
        self.hide()
