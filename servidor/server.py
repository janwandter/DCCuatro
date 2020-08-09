import socket 
import threading
import json
from collections import defaultdict
from time import sleep
import base64
import copy
from random import choice
from communication_tools import send_json, prepare_img
from logs import logs
import os
from generador_de_mazos import sacar_cartas

class Server:

    def __init__(self, port, host):
        self.port = port
        self.host = host
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockets = defaultdict(lambda: None) #Estan los sockets y tienen la info del username
        self.id = 1
        self.wait_room = {"type": "wait_room"} 
        self.wait_room["players"] = dict() #keys son nombres y values posiciones
        self.in_game = False
        self.taking = False
        self.shout_before = False
        self.players_cards = dict() #solo cantidad
        self.pile_card = None
        self.turn = list() #Se van eliminando los que van perdiendo
        self.player_turn = "1"
        self.plus_2 = 0
        self.shout_due = dict()
        self.parametros_open()
        self.bind_listen()
        self.accept_connections()
        self.online()


    def parametros_open(self):
        with open("parametros.json") as file:
            self.parametros = json.load(file)
    
########################### Server definition ###########################################    

    def bind_listen(self):
        self.socket_server.bind((self.host, self.port))
        self.socket_server.listen(8)
        print(f'server listening in {self.host} <> {self.port}')
        logs("ID", "Nombre", 99, "Descripción")
        temp = '{:^4} | {:^12} | {:^40} | {:^20} |'
        print(temp.replace(':', ':-').format('', '', '', ''))

    def accept_connections(self):
        thread = threading.Thread(target = self.accept_connections_thread, daemon = True)
        thread.start()

    def accept_connections_thread(self):
        while True:
            client_socket, address = self.socket_server.accept()
            self.sockets[client_socket] = {"address": address}
            self.sockets[client_socket]["id"] = f"{self.id}"
            logs(self.id, "", 1, "")
            self.id += 1
            listening_client_thread = threading.Thread( \
                target= self.listen_client_thread, \
                    args= (client_socket, ), \
                        daemon= True)
            listening_client_thread.start()
   
    def listen_client_thread(self, client_socket):
        try:
            while True:
                length = int.from_bytes(client_socket.recv(4), "little")
                response = client_socket.recv(length)
                recived = response.decode("utf-8")
                recived = json.loads(recived)
                self.decode_msg(recived, client_socket)
        except ConnectionError:
            if "username" in self.sockets[client_socket].keys():
                if self.sockets[client_socket]["username"] in self.wait_room["players"]:
                    position = self.wait_room["players"][self.sockets[client_socket]["username"]]
                    if self.in_game:
                        logs(self.sockets[client_socket]["id"], \
                            self.sockets[client_socket]["username"], 5, "")
                        self.turn.pop(self.turn.index(position))
                    elif not self.in_game:
                        logs(self.sockets[client_socket]["id"], \
                            self.sockets[client_socket]["username"], 4, "")
                    del self.wait_room["players"][self.sockets[client_socket]["username"]]
            logs(self.sockets[client_socket]["id"], self.sockets[client_socket]["username"], 2, "")
            del self.sockets[client_socket]
            for client in self.sockets:
                send_json(self.sockets, self.wait_room, client)
            return

    def online(self):
        while True:
            pass

################################# Comunication Tools ########################################

    def decode_msg(self, msg, client):
        if msg["type"] == 'login':
            self.login_revision(msg, client)
        if msg["type"] == "play_card":
            self.is_playable(msg, client)
        elif msg["type"] == "take_card":
            self.take_card(client)
        elif msg["type"] == "color_choice":
            self.color_choice_handler(msg)
            logs(self.sockets[client]["id"], self.sockets[client]["username"], 10, msg)
        elif msg["type"] == "shout":
            self.shout_handler(client)
        elif msg["type"] == "shout_take_card":
            self.shout_take_card(client)

    def send_cards(self, card, id_pile_or_mine):
        tipo = card[0].encode("utf-8", "ignore")
        color = card[1].encode("utf-8", "ignore")
        chunk = bytearray()
        chunk.extend((3).to_bytes(4, 'big'))
        chunk.extend((1).to_bytes(4, 'big'))
        chunk.extend((len(color)).to_bytes(4, 'little'))
        chunk.extend(color)
        chunk.extend((2).to_bytes(4, 'big'))
        chunk.extend((len(tipo)).to_bytes(4, 'little'))
        chunk.extend(tipo)
        nombre = f"{card[0]}_{card[1]}.png"
        if card[0] == "color":
            nombre = "color.png"
        chunk.extend(prepare_img(f"sprites/simple/{nombre}", id_pile_or_mine))
        if id_pile_or_mine == 4:
            self.pile_card = card
        return chunk

################################ Game Handlers ###########################################
    
    def login_revision(self, msg, client):
        existe = msg["username"] in self.wait_room["players"]
        alnum = msg["username"].isalnum()
        cupos = len(self.wait_room["players"]) < self.parametros["jugadores"]
        if existe or not alnum or not cupos or self.in_game:
            send_json(self.sockets, {"login": "False", "type": "login"}, client)
            logs(self.sockets[client]["id"], msg["username"], 3, False)
            return
        logs(self.sockets[client]["id"], msg["username"], 3, True)
        send_json(self.sockets, {"login": "True", "type": "login"}, client)
        self.sockets[client]["username"] = msg["username"]
        self.loading_players(msg)

    def loading_players(self, status):
        for position in range(1, self.parametros["jugadores"] + 1): #proximamanet parametros
            if f"{position}" not in self.wait_room["players"].values():    
                self.wait_room["players"][status['username']] = f"{position}"
                break
        for client in self.sockets.keys():
            send_json(self.sockets, self.wait_room, client)
        if len(self.wait_room["players"]) == self.parametros["jugadores"]: #paraemetros
            for client in self.sockets.keys():
                start_game = {"type": "start_game"}
                start_game["players"] = copy.deepcopy(self.wait_room["players"])
                send_json(self.sockets, start_game, client)
            self.prepare_game()

    def prepare_game(self):
        for position in range(1, self.parametros["jugadores"] + 1): #Parametros
            self.players_cards[f"{position}"] = 0
        chunk = bytearray()
        chunk.extend((4).to_bytes(4, 'big'))
        chunk.extend(prepare_img(os.path.join(*self.parametros["path_reverso"]), 11))
        chunk.extend(prepare_img(os.path.join(*self.parametros["path_reverso_izq"]), 13))
        chunk.extend(prepare_img(os.path.join(*self.parametros["path_reverso_der"]), 12))
        chunk.extend(prepare_img(os.path.join(*self.parametros["path_reverso_up"]), 14))
        for client in self.sockets.keys():
            client.sendall(chunk)
            logs(self.sockets[client]["id"], self.sockets[client]["username"], 8, "")
        data_fix = list()
        for position in range(1,4):
            data = {
                "type": "add_oponents_cards", 
                "player": f"{position}",
                "n_cards": "0",
                "cards_to_add": "5", 
                "add": "True"}
            data_fix.append(data)
            self.shout_due[f"{position}"] = 0
        for client in self.sockets.keys():
            send_json(self.sockets, data_fix, client)
        self.pile_card = sacar_cartas(1)[0]
        if self.pile_card[1] == '':
            colores = ["amarillo", "verde", "azul", "rojo"]
            color_pile = choice(colores)
            self.pile_card = ("color", color_pile)
        for client in self.sockets.keys():
            cartas = sacar_cartas(5)
            for carta in cartas:
                client.sendall(self.send_cards(carta, 3))
                logs(self.sockets[client]["id"], self.sockets[client]["username"], 7, carta)
            client.sendall(self.send_cards(self.pile_card, 4))
        for turno in range(1,4): #parametros
            self.turn.append(f"{turno}")
            self.players_cards[f"{turno}"] = 5
                    
    def is_playable(self, data, client):
        aprove = False
        change = 1
        logs(self.sockets[client]["id"], self.sockets[client]["username"], 9, data)
        if self.shout_due[self.player_turn] > 0:
            return
        if self.pile_card[0] == "+2":
            if data["tipo"] == "+2" and not self.taking:
                self.plus_2 += 2
                aprove = True
            if data["color"] == self.pile_card[1] and self.plus_2 == 0:
                aprove = True
            elif data["tipo"] == "color" and self.plus_2 == 0:
                aprove = True
                if len(self.pile_card[1]) > 0:
                    choice_data = {"type": "color_choice"}
                    send_json(self.sockets, choice_data, client)
                    aprove = True
        elif data["tipo"] == "color":
            if len(self.pile_card[1]) > 0:
                choice_data = {"type": "color_choice"}
                send_json(self.sockets, choice_data, client)
                aprove = True
        elif data["tipo"] == "sentido":
            if data["color"] == self.pile_card[1] or self.pile_card[0] == "sentido":
                aprove = True
                change = -1
        else:
            if data["tipo"] == self.pile_card[0] or data["color"] == self.pile_card[1]:
                if data["tipo"] == "+2":
                    self.plus_2 += 2
                aprove = True
        if aprove:
            turn = self.player_turn
            self.turn_handler(change)
            bytearray_img = self.send_cards((data["tipo"], data["color"]), 4)
            for user in self.sockets.keys():
                user.sendall(bytearray_img)
            new_data = {
                "type": "add_oponents_cards", 
                "player": f"{turn}",
                "n_cards": f"{self.players_cards[turn]}",
                "cards_to_add": "0", 
                "add": "False",
                "turn": self.player_turn,
                "+2": max(1, self.plus_2)}
            self.players_cards[turn] -= 1
            for user in self.sockets.keys():
                send_json(self.sockets, new_data, user)
            if self.players_cards[turn] == 0:
                send_json(self.sockets, {"type": "end", "win": "True"}, client)
                for cliente in self.sockets.keys():
                    if cliente != client:
                        send_json(self.sockets, {"type": "end", "win": "False"}, cliente)
                self.wait_room["players"] = {}
                self.turn = []
    
    def take_card(self, client):
        logs(self.sockets[client]["id"], self.sockets[client]["username"], 6, "")
        self.taking = True
        turn = self.player_turn
        if self.players_cards[turn] >= 10:
            self.exceed_cards(turn, client)
            self.plus_2 = 0
            return
        elif self.players_cards[turn] == 1:
            self.shout_before = False
        carta = sacar_cartas(1)
        logs(self.sockets[client]["id"], self.sockets[client]["username"], 7, carta[0])
        img_chunk = self.send_cards(carta[0], 3)
        client.sendall(img_chunk)
        if self.plus_2 > 0:
            self.plus_2 -= 1
            self.taking = True
        if self.plus_2 == 0:
            self.turn_handler(1)
            self.taking = False
        data = {
                "type": "add_oponents_cards", 
                "player": f"{turn}",
                "n_cards": f"{self.players_cards[turn]}",
                "cards_to_add": "1", 
                "add": "True",
                "turn": self.player_turn,
                "+2": max(1, self.plus_2)}
        self.players_cards[turn] += 1
        for client in self.sockets.keys():
            send_json(self.sockets, data, client)
    
    def shout_take_card(self, client):
        logs(self.sockets[client]["id"], self.sockets[client]["username"], 12, "")
        position = self.wait_room["players"][self.sockets[client]["username"]]
        if self.players_cards[position] >= 10:
            self.exceed_cards(position, client)
            return
        elif self.players_cards[position] == 1:
            self.shout_before = False
        carta = sacar_cartas(1)
        img_chunk = self.send_cards(carta[0], 3)
        client.sendall(img_chunk)
        if self.shout_due[position] > 0:
            self.shout_due[position] -= 1
        if self.shout_due[position] == 0:
            self.taking = False
        data = {
                "type": "add_oponents_cards", 
                "player": f"{position}",
                "n_cards": f"{self.players_cards[position]}",
                "cards_to_add": "1", 
                "add": "True",
                "shout": self.shout_due[position]}
        self.players_cards[position] += 1
        for client in self.sockets.keys():
            send_json(self.sockets, data, client)

    def shout_handler(self, client):
        logs(self.sockets[client]["id"], self.sockets[client]["username"], 11, "")
        position = self.wait_room["players"][self.sockets[client]["username"]]
        count = 0
        for players in self.players_cards:
            if self.players_cards[players] == 1:
                count += 1
        only_me = (count == 1 and self.players_cards[position] == 1)
        are_others = not (only_me or count == 0)
        if only_me and not self.shout_before:
            self.shout_before = True
            return
        elif are_others and not self.shout_before:
            position_copy = position
            position = choice([user for user in self.players_cards\
                if self.players_cards[user] == 1 and user != position_copy])
            self.shout_before = True
        data = {"type": "shout_response", "position": position}
        for client in self.sockets.keys():
            send_json(self.sockets, data, client)
        self.shout_due[position] = self.parametros["shout_due_cards"]

    def turn_handler(self, change): 
        if change < 0:
            self.turn.reverse()
        if self.player_turn != self.turn[-1]:
            self.player_turn = self.turn[self.turn.index(self.player_turn) + 1]
        else:
            self.player_turn = self.turn[0]

    def exceed_cards(self, position, client):
        self.taking = False
        data = {"type": "espectator", "player": position}
        for client in self.sockets.keys():
            send_json(self.sockets, data, client)
        self.turn_handler(1)
        self.turn.pop(self.turn.index(position))
        self.plus_2 = 0
        data = {
            "type": "add_oponents_cards", 
            "player": f"{position}",
            "n_cards": f"{self.players_cards[position]}",
            "cards_to_add": "0", 
            "add": "True",
            "turn": self.player_turn,
            "+2": 1}
        for client in self.sockets.keys():
            send_json(self.sockets, data, client)
        if len(self.turn) == 1:
            for user in self.sockets:
                position = self.wait_room["players"][self.sockets[user]["username"]]
                if position == self.turn[0]:
                    send_json(self.sockets, {"type": "end", "win": "True"}, user)
                    break
            for cliente in self.sockets.keys():
                if cliente != user:
                    send_json(self.sockets, {"type": "end", "win": "False"}, cliente)
            self.wait_room["players"] = {}
            self.turn = []

    def color_choice_handler(self, msg):
        nuevo_color = ("color", msg["color"])
        msg = self.send_cards(nuevo_color, 4)
        for client in self.sockets.keys():
            client.sendall(msg)

if __name__ == '__main__':
    with open("parametros.json") as file:
        param_json = json.load(file)
    port = param_json["port"]
    host = param_json["host"]
    server = Server(port, host)


