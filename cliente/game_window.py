import sys
import json
from PyQt5 import uic
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QCoreApplication
from PyQt5.QtWidgets import QApplication, QDialog, QSizePolicy
from PyQt5.QtGui import QPixmap, QTransform, QFont

window_name, base_class = uic.loadUiType("game_window.ui")

class GameWindow(window_name, base_class):

    select_card_signal = pyqtSignal(tuple)
    shout_signal = pyqtSignal()
    take_card_signal = pyqtSignal(bool)
    color_answer_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.shout_button.clicked.connect(self.shout)
        self.turn = "1"
        self.deck_card = "1" 
        self.shout_loss = False
        self.deck = dict()
        self.my_cards = dict()
        self.left = dict()
        self.up = dict()
        self.right = dict()
        self.me = dict()
        self.my_view = dict()
        self.reverse = dict()
        ####################################################
        self.labels_to_dict()
        self.parametros()

    def end_game(self):
        for player in self.my_view:
            for carta in self.my_view[player]:
                self.my_view[player][carta].setPixmap(QPixmap(None))

        self.hide()

    def shout(self):
        self.shout_signal.emit()
    
    def espectate(self, player):
        self.shout_loss = False
        self.shout_text.setText(f"")
        lose_dialog = LoseDialog(self.usernames[player])
        for carta in self.my_view[player]:
            self.my_view[player][carta].setPixmap(QPixmap(None))
        if player == self.my_pos:
            self.shout_button.setEnabled(False)
        lose_dialog.exec_()
    
    def shout_response(self, position):
        self.shout_text.setText(f"{self.usernames[position]} saca"
        f" 4 cartas por ¡DCCuatro!")
        if position == self.my_pos:
            self.shout_loss = True
    
    def start_game(self, players, my_pos):
        self.my_display(my_pos)
        self.my_pos = my_pos
        self.usernames = dict()
        self.shout_button.setEnabled(True)
        for jugador in players:
            if players[jugador] == self.my_left:
                self.p_text_left.setText(jugador)
                self.usernames[self.my_left] = jugador 
            elif players[jugador] == self.my_up:
                self.p_text_up.setText(jugador)
                self.usernames[self.my_up] = jugador
            elif players[jugador] == self.my_right:
                self.p_text_right.setText(jugador)
                self.usernames[self.my_right] = jugador
            elif players[jugador] == self.my_pos:
                self.p_text_me.setText(jugador)
                self.usernames[self.my_pos] = jugador
        self.player_turn.setText(self.usernames[self.turn])
        self.show()
        pass

    def mousePressEvent(self, evento):
        if self.turn == self.my_pos:
            if evento.y() > self.p["card_y"]:
                for carta in self.me:
                    x = self.my_view[self.my_pos][carta].x()
                    y = self.p["card_y"]
                    if  x < evento.x() < x + self.p["card_width"] and \
                        y < evento.y() < y + self.p["card_height"]:
                        if self.my_cards[carta] is not None:
                            carta_elegida = self.my_cards[carta]
                            self.select_card_signal.emit(carta_elegida)
                            self.card_election = carta
        if self.turn == self.my_pos or self.shout_loss:
            if self.p["deck_y_top"] < evento.y() < self.p["deck_y_base"] and\
                 self.p["deck_x_base"] < evento.x() < self.p["deck_x_top"]:
                self.deck_change()
                self.take_card_signal.emit(self.shout_loss)

    def add_remove_card(self, data):
        player = data["player"]
        n_cards = int(data["n_cards"])
        cards_to_add = int(data["cards_to_add"])
        add = self.str_to_bool(data["add"])
        if "turn" in data.keys():
            self.turn = data["turn"]
            self.player_turn.setText(self.usernames[self.turn])
        if "+2" in data.keys():
            self.n_cards_text.setText(f'{data["+2"]} cartas')
        if "shout" in data.keys():
            self.shout_text.setText(f"{self.usernames[data['player']]} saca"
                f" {data['shout']} cartas por ¡DCCuatro!")
            if data["shout"] == 0:
                self.shout_text.setText("")
                self.shout_loss = False 
        if player == self.my_pos:
            if not add and self.my_cards[self.card_election] is not None:
                self.my_cards[self.card_election] = None
                self.my_view[self.my_pos][self.card_election].setPixmap(QPixmap(None))   
            return
        elif player == self.my_left:
            orientation = "izq"
        elif player == self.my_up:
            orientation = "up"
        else:
            orientation = "der"
        if add:
            for card in range(n_cards + 1, n_cards + 1 + cards_to_add):
                self.my_view[player][str(card)].setPixmap(self.reverse[orientation])
            self.deck_change() 
        else: 
            self.my_view[player][f"{n_cards}"].setPixmap(QPixmap(None))

    def add_my_cards(self, info, img):
        imagen = QPixmap()
        imagen.loadFromData(img, 'png')
        for carta in self.my_cards:
            if self.my_cards[carta] == None:
                self.my_cards[carta] = info
                break
        self.my_view[self.my_pos][carta].setPixmap(imagen)

    def pile_card(self, color, img):
        imagen = QPixmap()
        imagen.loadFromData(img, 'png')
        self.playing_card.setPixmap(imagen)
        self.color.setText(color)
    
    def color_choice(self):
        dialog = ColorDialog()
        dialog.color_answer_signal = self.color_answer_signal
        dialog.exec_()
    
    def deck_change(self):
        self.deck[self.deck_card].setPixmap(QPixmap(None))
        if self.deck_card == "5":
            self.deck_card = "1"
            for deck_card in self.deck:
                self.deck[deck_card].setPixmap(self.reverse["me"])
        else:
            self.deck_card = f"{int(self.deck_card) + 1}"
        
    def save_reverse(self, id_, reverse_str):
        if id_ == 11:
            self.reverse["me"] = QPixmap()
            self.reverse["me"].loadFromData(reverse_str, 'png')
        elif id_ == 12:
            self.reverse["der"] = QPixmap()
            self.reverse["der"].loadFromData(reverse_str, 'png')
        elif id_ == 13:
            self.reverse["izq"] = QPixmap()
            self.reverse["izq"].loadFromData(reverse_str, 'png')
        elif id_ == 14:
            self.reverse["up"] = QPixmap()
            self.reverse["up"].loadFromData(reverse_str, 'png')

    def my_display(self, my_pos):
        if my_pos == "1":
            self.my_left = "2"
            self.my_up = "3"
            self.my_right = "4"
        elif my_pos == "2":
            self.my_left = "3"
            self.my_up = "4"
            self.my_right = "1"
        elif my_pos == "3":
            self.my_left = "4"
            self.my_up = "1"
            self.my_right = "2"
        elif my_pos == "4":
            self.my_left = "1"
            self.my_up = "2"
            self.my_right = "3"
        self.my_view[self.my_left] = self.left
        self.my_view[self.my_up] = self.up
        self.my_view[self.my_right] = self.right
        self.my_view[my_pos] = self.me
        for cartas in range(1,11):
            self.my_cards[f"{cartas}"] = None
        self.deck["1"] = self.deck_1
        self.deck["2"] = self.deck_2
        self.deck["3"] = self.deck_3
        self.deck["4"] = self.deck_4
        self.deck["5"] = self.deck_5

    def labels_to_dict(self):
        self.left["1"] = self.left_1
        self.left["2"] = self.left_2
        self.left["3"] = self.left_3
        self.left["4"] = self.left_4
        self.left["5"] = self.left_5
        self.left["6"] = self.left_6
        self.left["7"] = self.left_7
        self.left["8"] = self.left_8
        self.left["9"] = self.left_9
        self.left["10"] = self.left_10
        self.up["1"] = self.up_1
        self.up["2"] = self.up_2
        self.up["3"] = self.up_3
        self.up["4"] = self.up_4
        self.up["5"] = self.up_5
        self.up["6"] = self.up_6
        self.up["7"] = self.up_7
        self.up["8"] = self.up_8
        self.up["9"] = self.up_9
        self.up["10"] = self.up_10
        self.right["1"] = self.right_1
        self.right["2"] = self.right_2
        self.right["3"] = self.right_3
        self.right["4"] = self.right_4
        self.right["5"] = self.right_5
        self.right["6"] = self.right_6
        self.right["7"] = self.right_7
        self.right["8"] = self.right_8
        self.right["9"] = self.right_9
        self.right["10"] = self.right_10
        self.me["1"] = self.p_card_1
        self.me["2"] = self.p_card_2
        self.me["3"] = self.p_card_3
        self.me["4"] = self.p_card_4
        self.me["5"] = self.p_card_5
        self.me["6"] = self.p_card_6
        self.me["7"] = self.p_card_7
        self.me["8"] = self.p_card_8
        self.me["9"] = self.p_card_9
        self.me["10"] = self.p_card_10

    def str_to_bool(self, str_cambiar):
        return str_cambiar != "False"
    
    def parametros(self):
        with open("parametros.json") as file:
            self.p = json.load(file)

class LoseDialog(QDialog):

    def __init__(self, player):
        super().__init__()
        self.player = player
        self.parametros()
        self.init_gui()

    def init_gui(self):
        self.setWindowTitle('Participante eliminado')
        self.setStyleSheet("background-color: rgba(245, 103, 99, 1)")
        self.resize(self.p["width_espectate"], self.p["height_espectate"]) 
        self.text = QLabel(f"{self.player} ha entrado en modo espectador", self)
        self.text.setStyleSheet("color: rgba(247, 227, 90, 1)")
        self.text.setFont(QFont("SansSerif", 12))
        self.text.setAlignment(Qt.AlignCenter)
        hbox = QHBoxLayout()
        hbox.addWidget(self.text)
        self.setLayout(hbox)
    
    def parametros(self):
        with open("parametros.json") as file:
            self.p = json.load(file)

class ColorDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.parametros()
        self.init_gui()
        
    def init_gui(self):
        self.setWindowTitle('Elegir carta')
        self.setStyleSheet("background-color: grey")
        self.resize(self.p["width_color_dialog"], self.p["height_color_dialog"])
        self.color_rojo = QPushButton(self)
        self.color_azul = QPushButton(self)
        self.color_verde = QPushButton(self)
        self.color_amarillo = QPushButton(self)
        self.color_rojo.setText("rojo")
        self.color_azul.setText("azul")
        self.color_verde.setText("verde")
        self.color_amarillo.setText("amarillo")
        self.color_rojo.setStyleSheet(f""
        f"background-color: rgba(245, 103, 99, 1); color: rgba(0, 0, 0, 0)")
        self.color_azul.setStyleSheet(f""
        f"background-color: rgba(2, 195, 228, 1); color: rgba(0, 0, 0, 0)")
        self.color_verde.setStyleSheet(f""
        f"background-color: rgba(50, 226, 155, 1); color: rgba(0, 0, 0, 0)")
        self.color_amarillo.setStyleSheet(f""
        f"background-color: rgba(247, 227, 90, 1); color: rgba(0, 0, 0, 0)")
        self.choice_text = QLabel("Elige un color", self)
        self.choice_text.setAlignment(Qt.AlignCenter)
        self.choice_text.setFixedHeight(30)
        self.choice_text.setStyleSheet("color: white")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.color_rojo.setSizePolicy(sizePolicy)
        self.color_azul.setSizePolicy(sizePolicy)
        self.color_verde.setSizePolicy(sizePolicy)
        self.color_amarillo.setSizePolicy(sizePolicy)

        hbox_1 = QHBoxLayout()
        hbox_1.addWidget(self.color_rojo)
        hbox_1.addWidget(self.color_amarillo)

        hbox_2 = QHBoxLayout()
        hbox_2.addWidget(self.color_verde)
        hbox_2.addWidget(self.color_azul)

        vbox = QVBoxLayout()
        vbox.addWidget(self.choice_text)
        vbox.addLayout(hbox_1)
        vbox.addLayout(hbox_2)

        self.setLayout(vbox)

        self.color_rojo.clicked.connect(self.choice)
        self.color_verde.clicked.connect(self.choice)
        self.color_azul.clicked.connect(self.choice)
        self.color_amarillo.clicked.connect(self.choice)
   
    def choice(self):
        self.color_answer_signal.emit(self.sender().text())
        self.close()

    def parametros(self):
        with open("parametros.json") as file:
            self.p = json.load(file)