import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QCoreApplication
from PyQt5.QtWidgets import QApplication, QDialog, QSizePolicy
from PyQt5.QtGui import QPixmap, QTransform


window_name, base_class = uic.loadUiType("summary.ui")

class SummaryWindow(window_name, base_class):

    relogin_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.relogin_button.clicked.connect(self.relogin)
    
    def player_summary(self, winner, name):
        if winner:
            return self.winner(name)
        self.loser(name)
            
    def winner(self, name):
        self.lose.setPixmap(QPixmap(None))
        self.win.setPixmap(QPixmap("sprites/Logo_1.png"))
        self.crown.setPixmap(QPixmap("sprites/crown_win.png"))
        self.win.setScaledContents(True)
        self.crown.setScaledContents(True)
        self.summary_text.setText(f"¡{name} HAS GANADO!")
        self.show()
        return
    
    def loser(self, name):
        self.lose.setPixmap(QPixmap("sprites/lose.png"))
        self.lose.setScaledContents(True)
        self.win.setPixmap(QPixmap(None))
        self.crown.setPixmap(QPixmap(None))
        self.summary_text.setText(f"¡{name} HAS PERDIDO!")
        self.show()

    def relogin(self):
        self.relogin_signal.emit()
        self.hide()

    