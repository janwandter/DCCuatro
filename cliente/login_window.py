import sys
import os
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QLineEdit, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QCoreApplication
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QPixmap


class LoginWindow(QWidget):

    login_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def init_gui(self):
        self.setWindowTitle("Login DCCuatro")
        self.setGeometry(650, 200, 480, 720)

        self.background = QLabel(self)
        path = os.path.join("sprites", "login.png")
        pixeles_back = QPixmap(path)
        self.background.setPixmap(pixeles_back)
        self.background.resize(480, 720)
        self.background.setScaledContents(True)
        
        self.user_edit = QLineEdit('', self)
        self.user_edit.setPlaceholderText('Ingrese su nombre de usuario')
        self.user_edit.setFont(QFont("SansSerif", 12, weight=QFont.Bold))
        self.user_edit.resize(350, 30)
        self.user_edit.move(75, 600)

        self.log_button = QPushButton('Entrar', self)
        self.log_button.setFont(QFont("SansSerif", 12))
        self.log_button.setStyleSheet("background-color: red;\
             color: yellow;")
        self.log_button.resize(80, 30)
        self.log_button.move(350, 600)
        
        self.log_button.clicked.connect(self.login)
        self.show()

    def login(self):
        self.login_signal.emit(self.user_edit.text())

    def login_answer(self, permission):
        if permission:
            self.hide()
            return
        self.user_edit.clear()
        self.user_edit.setPlaceholderText('Error: no has podido entrar')
    
    def relogin(self):
        self.init_gui()