import socket
import sys
import threading
import json
import base64
from PyQt5.QtCore import QThread, pyqtSignal

class Cliente(QThread):
    
    login_answer_signal = pyqtSignal(bool)
    wait_room_signal = pyqtSignal()
    update_wait_room_signal = pyqtSignal(dict) 
    start_game_signal = pyqtSignal(dict, str)
    close_wait_room_signal = pyqtSignal()
    prepare_game_signal = pyqtSignal(int, bytes)
    add_oponents_cards_signal = pyqtSignal(dict)
    add_my_cards_signal = pyqtSignal(tuple, bytes)
    pile_card_signal = pyqtSignal(str, bytes)
    color_choice_signal = pyqtSignal()
    end_game_signal = pyqtSignal()
    summary_signal = pyqtSignal(bool, str)
    shout_response_signal = pyqtSignal(str)
    espectate_signal = pyqtSignal(str)

    def __init__(self, port, host):
        super().__init__()
        self.port = port
        self.host = host
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.window = 'login'
        self.decoding = 'json'
        try:
            self.connect_to_server()
            self.listen()
            self.isConnected = True
        except ConnectionError:
            self.client_socket.close()
            self.isConnected = False
            exit()

    def connect_to_server(self):
        self.client_socket.connect((self.host, self.port))

    def listen(self):
        thread = threading.Thread(target = self.listen_thread, daemon = True)
        thread.start()

    def listen_thread(self):
        try:
            while True:
                decision = int.from_bytes(self.client_socket.recv(4), 'big')
                if decision == 0:
                    self.decoding = 'json'
                elif decision == 3:
                    self.decoding = 'bytearray'
                else:
                    self.decoding = 'reverse'
                if self.decoding == 'json':
                    length = int.from_bytes(self.client_socket.recv(4), 'little')
                    data = self.client_socket.recv(length)
                    decoded_data = data.decode("utf-8", "ignore")
                    decoded_data = decoded_data.replace('\'', '\"')
                    data = json.loads(decoded_data)
                    self.decode_server_msg(data)
                elif self.decoding == 'bytearray':
                    self.decoding = 'json'
                    for chunk in range(3):
                        id_b = self.client_socket.recv(4)
                        id_ = int.from_bytes(id_b, 'big')
                        length_b = self.client_socket.recv(4)
                        length = int.from_bytes(length_b, 'little')
                        img = self.client_socket.recv(length)
                        self.decode_server_bytearray(id_, img)
                elif self.decoding == 'reverse':
                    self.decoding = 'json'
                    for chunk in range(4):
                        id_b = self.client_socket.recv(4)
                        id_ = int.from_bytes(id_b, 'big')
                        length_b = self.client_socket.recv(4)
                        length = int.from_bytes(length_b, 'little')
                        img = self.client_socket.recv(length)
                        self.decode_server_bytearray(id_, img)
        except ConnectionResetError:
            print("El servidor se ha caido, estamos trabajando en ello")
            self.client_socket.close()
            self.isConnected = False
            exit()
            
    def send(self, msg):
        chunk = bytearray()
        json_msg = json.dumps(msg)
        msg_send = json_msg.encode("utf-8")
        chunk.extend((len(msg_send)).to_bytes(4, "little"))
        chunk.extend(msg_send)
        self.client_socket.send(chunk)

    def online(self):
        while self.isConnected:
            pass

    def run(self):
        self.online()

    def decode_server_msg(self, data):
        with threading.Lock():
            if type(data) == list:
                for dic in data:
                    if dic["type"] == "add_oponents_cards":
                        self.add_oponents_cards_signal.emit(dic)
                return
            if data["type"] == 'login':
                self.server_login_answer(data["login"])
            elif data["type"] == 'wait_room' and self.window == 'wait_room':
                self.update_wait_room_signal.emit(data["players"])
            elif data["type"] == 'start_game':
                self.start_game_signal.emit(data["players"], data["players"][self.username])
                self.close_wait_room_signal.emit()
            elif data["type"] == 'add_oponents_cards':
                self.add_oponents_cards_signal.emit(data)
            elif data["type"] == 'color_choice':
                self.color_choice_signal.emit()
            elif data["type"] == 'end':
                self.end_game_signal.emit()
                win = self.str_to_bool(data["win"])
                self.summary_signal.emit(win, self.username)
                self.window = 'login'
            elif data["type"] == 'shout_response':
                self.shout_response_signal.emit(data["position"])
            elif data["type"] == 'espectator':
                self.espectate_signal.emit(data["player"])
            
    def decode_server_bytearray(self, id_, img_bytes):
        with threading.Lock():
            if id_ > 10:
                img = base64.b64decode(img_bytes)
                self.prepare_game_signal.emit(id_, img)
            elif id_ == 1:
                self.color = img_bytes.decode("utf-8", "ignore")
            elif id_ == 2:
                self.tipo = img_bytes.decode("utf-8", "ignore")
            elif id_ == 3:
                img = base64.b64decode(img_bytes)
                self.add_my_cards_signal.emit((self.tipo, self.color), img)
            elif id_ == 4:
                img = base64.b64decode(img_bytes)
                self.pile_card_signal.emit(self.color, img)
        return

    def login_permission(self, user):
        data = {"type": "login", "username": user}
        self.username = user
        self.send(data)

    def server_login_answer(self, permission):
        access = self.str_to_bool(permission)
        self.login_answer_signal.emit(access)
        if access:
            self.window = 'wait_room'
            self.wait_room_signal.emit()

    def str_to_bool(self, str_cambiar):
        return str_cambiar != "False"

    ############################# back-end ######################################

    def select_card(self, card):
        data = {"type": "play_card", "tipo": card[0], "color": card[1]}
        self.send(data)

    def shout(self):
        data = {"type": "shout"}
        self.send(data)

    def take_card(self, shout):
        data = {"type": "take_card"}
        if shout:
            data = {"type": "shout_take_card"}
        self.send(data)

    def choice_color(self, color):
        data = {"type": "color_choice", "color": color}
        self.send(data)
