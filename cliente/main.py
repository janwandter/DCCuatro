import sys
from login_window import LoginWindow
from waiting_room import WaitingRoom
from game_window import GameWindow
from summary_window import SummaryWindow
from client import Cliente
from PyQt5.QtWidgets import QApplication

game = QApplication([])

port = 8816
host = 'localhost'

cliente = Cliente(port, host)
cliente.start()

log_window = LoginWindow()
wait_room = WaitingRoom()
game_win = GameWindow()
summary = SummaryWindow()
log_window.init_gui()


log_window.login_signal.connect(cliente.login_permission)
cliente.wait_room_signal.connect(wait_room.init_gui)
cliente.login_answer_signal.connect(log_window.login_answer)
cliente.update_wait_room_signal.connect(wait_room.update_players)
cliente.start_game_signal.connect(game_win.start_game)
cliente.close_wait_room_signal.connect(wait_room.close)
cliente.prepare_game_signal.connect(game_win.save_reverse)
cliente.add_oponents_cards_signal.connect(game_win.add_remove_card)
cliente.add_my_cards_signal.connect(game_win.add_my_cards)
cliente.pile_card_signal.connect(game_win.pile_card)
game_win.select_card_signal.connect(cliente.select_card)
game_win.take_card_signal.connect(cliente.take_card)
cliente.color_choice_signal.connect(game_win.color_choice)
game_win.color_answer_signal.connect(cliente.choice_color)
cliente.end_game_signal.connect(game_win.end_game)
cliente.summary_signal.connect(summary.player_summary)
summary.relogin_signal.connect(log_window.relogin)
game_win.shout_signal.connect(cliente.shout)
cliente.shout_response_signal.connect(game_win.shout_response)
cliente.espectate_signal.connect(game_win.espectate)



sys.exit(game.exec_())