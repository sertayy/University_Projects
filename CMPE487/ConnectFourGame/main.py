import math
import threading
import socket
import json
import time
import pygame
import sys
import PySimpleGUI as Sg
import frontend as fe
from game import Game, Color
from multiprocessing import Process, Manager, Value
from typing import List
import os

home_window = None
USERNAME_IP: dict = {}  # username -> IP
MY_IP: str = os.popen("ipconfig getifaddr en0").read()[:-1]
MY_NAME: str = ""
PROGRAM_STATUS: bool = True
GAME_STATUS: bool = True
PORT_DEFAULT: int = 12345
PORT_GAME: int = 1234
CHAT_HISTORY: dict = {}  # list of messages from the player we are currently messaging with, as queue
CHAT_MODE: bool = False
OPPONENT_MOVES = []  # list of coordinates, representing opp_name's move -> tuples (row, col)

coordination_package = {
    "NAME": MY_NAME,
    "MY_IP": MY_IP,
    "TYPE": "COORDINATION",
    "COL": -1,
    "ROW": -1
}

game_package = {
    "NAME": MY_NAME,
    "MY_IP": MY_IP,
    "INVITATION": False,
    "TYPE": "GAME",
    "RESPOND": False
}

respond_package = {
    "NAME": MY_NAME,
    "MY_IP": MY_IP,
    "TYPE": "RESPOND",
    "PAYLOAD": ""
}

message_package = {
    "NAME": MY_NAME,
    "MY_IP": MY_IP,
    "TYPE": "MESSAGE",
    "PAYLOAD": "",
    "IS_GAME": False
}

discovery_package = {
    "NAME": MY_NAME,
    "MY_IP": MY_IP,
    "TYPE": "DISCOVER",
    "PAYLOAD": ""
}

goodbye_package = {
    "NAME": MY_NAME,
    "MY_IP": MY_IP,
    "TYPE": "GOODBYE",
    "PAYLOAD": ""
}


def send_discovery():
    """Sends a broadcast discovery message with UDP"""
    for i in range(3):
        send_package_UDP(discovery_package, "<broadcast>")


def send_goodbye():
    """Sends a broadcast goodbye message with UDP"""
    for i in range(3):
        send_package_UDP(goodbye_package, "<broadcast>")


def send_game_invitation(username: str):
    """Calls the send_package_TCP function with type GAME/INVITATION"""
    invitation: dict = game_package
    invitation['INVITATION'] = True
    invitation['RESPOND'] = False
    send_package_TCP(username, invitation)


def send_coordinates(username: str, col: int, row: int):
    """Sends the coordinates of the disc"""
    cp: dict = coordination_package
    cp['COL'] = col
    cp['ROW'] = row
    send_package_TCP(username, cp)


def send_message(username: str, payload: str, user_ip: str = None, my_name: str = None):
    """Calls the send_package_TCP function with type MESSAGE"""
    message: dict = message_package
    message["PAYLOAD"] = payload
    if user_ip is None:
        send_package_TCP(username, message)
    else:
        message["NAME"] = my_name
        message["IS_GAME"] = True
        send_package_in_game(username, user_ip, message)


def send_package_UDP(package: dict, recv_ip: str):
    """Sends a UDP package"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto((json.dumps(package) + "\n").encode(encoding='UTF-8'), (recv_ip, PORT_DEFAULT))
            s.close()
        except Exception as ex:
            print('\033[91m' + "ERROR(send_package_UDP): Error occurred during outgoing UDP -> {0}".format(ex)
                  + '\033[0m')


def send_package_TCP(username: str, packet: dict):
    """Sends a TCP package"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect((USERNAME_IP[username], PORT_DEFAULT))
            s.sendall((json.dumps(packet) + "\n").encode(encoding='UTF-8'))
        except Exception as ex:
            print('\033[91m' + "ERROR(send_package_TCP): Couldn't send a packet to {0} due to: {1}".format(username, ex)
                  + '\033[0m')


def send_package_in_game(username: str, opp_ip: str, packet: dict):
    """Sends a TCP chat package while in game"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect((opp_ip, PORT_GAME))
            s.sendall((json.dumps(packet) + "\n").encode(encoding='UTF-8'))
        except Exception as ex:
            print('\033[91m' + "ERROR(send_package_in_game): Couldn't send a packet to {0} due to: {1}"
                  .format(username, ex) + '\033[0m')


def incoming_coordinates(package: dict):
    """Gets the opponents move"""
    opponent_col = package["COL"]
    opponent_row = package["ROW"]
    OPPONENT_MOVES.append((opponent_row, opponent_col))


def incoming_game_invitation(package: dict):
    """Alerts main process to show pop-up"""
    home_window.write_event_value(key='Incoming Game Invitation', value=package["NAME"])


def incoming_game_response(package: dict):
    """Alerts the main process to show pop up according to the response"""
    if package["RESPOND"]:
        home_window.write_event_value(key='Accepted Game Response', value=package["NAME"])
    else:
        home_window.write_event_value(key='Declined Game Response', value=package["NAME"])


def incoming_message(package: dict):
    """Updates the chat history or alerts main process to show a pop up"""
    if package["NAME"] not in CHAT_HISTORY.keys():
        CHAT_HISTORY[package["NAME"]] = [package["PAYLOAD"]]
    else:
        CHAT_HISTORY[package["NAME"]].append(package["PAYLOAD"])
    if not CHAT_MODE:
        home_window.write_event_value(key='Incoming Chat', value=[package["NAME"], package["PAYLOAD"]])


def incoming_respond(package: dict):
    """Adds the user to the user list"""
    USERNAME_IP[package["NAME"]] = package["MY_IP"]


def incoming_goodbye(package: dict):
    """Deletes the user from the user list and alerts main process to show a pop up"""
    if package["NAME"] in USERNAME_IP:
        del USERNAME_IP[package["NAME"]]
        home_window.write_event_value(key='Goodbye', value=package["NAME"])


def incoming_discovery(package: dict):
    """Sends respond to the incoming discovery message and adds the user to the user list"""
    USERNAME_IP[package["NAME"]] = package["MY_IP"]
    send_package_TCP(package["NAME"], respond_package)


def runner_server_UDP():  # listen UDP, for udp discovery
    """Listens udp packets such as goodbye and discovery"""
    global PROGRAM_STATUS
    while PROGRAM_STATUS:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as server:
            try:
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                server.settimeout(2)
                if not PROGRAM_STATUS:
                    break
                server.bind(("", PORT_DEFAULT))
                data, addr = server.recvfrom(1024)
                current = data.decode(encoding='UTF-8')
                json_message = json.loads(str(current))
                handle_msg(json_message)
            except socket.timeout:
                pass
            except Exception as ex:
                print('\033[91m' + "ERROR(runner_server_UDP): Error happened in runner_server_UDP function --> {0}"
                      .format(ex) + '\033[0m')


def runner_server_TCP():
    """Listens tcp packets"""
    global PROGRAM_STATUS
    while PROGRAM_STATUS:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            try:
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.settimeout(2)
                if not PROGRAM_STATUS:
                    break
                server.bind((MY_IP, PORT_DEFAULT))
                server.listen()
                conn, addr = server.accept()
                with conn:
                    cumulative = ""
                    while True:
                        data = conn.recv(1024)
                        current = data.decode(encoding='UTF-8')
                        if not data:
                            break
                        conn.sendall(data)
                        cumulative = cumulative + current
                    json_message = json.loads(str(cumulative))
                    handle_msg(json_message)
            except socket.timeout:
                pass
            except Exception as ex:
                print('\033[91m' + "ERROR(runner_server_TCP): Error happened in runner_server_TCP function --> {0}"
                      .format(ex) + '\033[0m')


def helper_server_TCP(game_chat):
    """Listens the message packets sent in game"""
    global GAME_STATUS
    while GAME_STATUS:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            try:
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.settimeout(2)
                if not GAME_STATUS:
                    break
                server.bind((MY_IP, PORT_GAME))
                server.listen()
                conn, addr = server.accept()
                with conn:
                    cumulative = ""
                    while True:
                        data = conn.recv(1024)
                        current = data.decode(encoding='UTF-8')
                        if not data:
                            break
                        conn.sendall(data)
                        cumulative = cumulative + current
                    json_message = json.loads(str(cumulative))
                    game_chat.append(json_message["PAYLOAD"])
            except socket.timeout:
                pass
            except Exception as ex:
                print('\033[91m' + "ERROR(helper_server_TCP): Error happened in helper_server_TCP function --> {0}"
                      .format(ex) + '\033[0m')


def chat_page(opp_username: str, my_username: str, opp_ip: str = None, pos_x: int = None, pos_y: int = None,
              game_chat: List[str] = None, game_over: Value = None):
    """Chat page visual"""
    global CHAT_MODE
    CHAT_MODE = True
    cumulative_message: str = ""
    if game_over is not None:
        close_button = "Leave Game"
    else:
        close_button = "Close Window"
    layout = [[Sg.Text('Chat:\t\t'), Sg.Text('Send Message to {0}'.format(opp_username))],
              [Sg.Multiline(size=(20, 3), key='CHAT_HISTORY', autoscroll=True, disabled=True),
               Sg.Multiline(size=(20, 3), key='textbox', enter_submits=True)],
              [Sg.Button('Send'), Sg.Button(close_button)]]  # identify the multiline via key option

    window = Sg.Window('Chat Window', layout, keep_on_top=True, location=(pos_x, pos_y))
    while True:
        event, values = window.read(timeout=1000)
        if event in (None, Sg.WIN_CLOSED, 'Close Window', 'Leave Game'):  # if user closes window or clicks cancel
            break
        elif event == 'Send':
            my_message = str(my_username + ": " + values['textbox'])
            cumulative_message = cumulative_message + my_message
            if opp_ip is None:
                send_message(opp_username, my_message)
            else:
                send_message(opp_username, my_message, opp_ip, my_username)
            window['CHAT_HISTORY'].update(cumulative_message)
            window['textbox'].update("")
        elif opp_ip is None and opp_username in CHAT_HISTORY:
            while CHAT_HISTORY[opp_username]:
                last_message = CHAT_HISTORY[opp_username].pop(0)
                cumulative_message = cumulative_message + last_message
                window['CHAT_HISTORY'].update(cumulative_message)
        elif opp_ip is not None:
            while game_chat:
                last_message = game_chat.pop(0)
                cumulative_message = cumulative_message + last_message
                window['CHAT_HISTORY'].update(cumulative_message)
    window.close()
    CHAT_MODE = False
    if close_button == "Leave Game":
        game_over.value = True


def game_page(opp_name: str, turn: int, game_over: Value):
    """Game page visual"""
    is_quit = False
    pygame.init()
    current_game = Game(6, 7, 100)
    current_game.font = pygame.font.SysFont("monospace", 75)
    current_game.screen = pygame.display.set_mode((current_game.width, current_game.height))
    game_over.value = False
    pygame.draw.rect(current_game.screen, Color.black, (0, 0, current_game.width, current_game.square_size))
    current_game.display_matrix()
    pygame.display.update()
    while not game_over.value:
        event = pygame.event.wait()

        if event.type == pygame.QUIT:
            pygame.quit()
            is_quit = True
            game_over.value = True
            break

        elif event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(current_game.screen, Color.black, (0, 0, current_game.width, current_game.square_size))
            pos_x = event.pos[0]
            if turn == 1:
                pygame.draw.circle(current_game.screen, Color.red, (pos_x, int(current_game.square_size / 2)),
                                   current_game.radius)
                pygame.display.update()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(current_game.screen, Color.black, (0, 0, current_game.width, current_game.square_size))
            if turn == 1:
                pos_x = event.pos[0]
                col = int(math.floor(pos_x / current_game.square_size))

                if current_game.matrix[current_game.row_count - 1][col] == 0:
                    row = current_game.available_row(col)
                    current_game.matrix[row][col] = 1
                    send_coordinates(opp_name, col, row)

                    if current_game.is_game_over(1):
                        label = current_game.font.render("YOU WON!!", True, Color.red)
                        current_game.screen.blit(label, (40, 10))
                        game_over.value = True
                    else:
                        turn = 2

                    current_game.display_matrix()
                    pygame.display.update()

        while turn == 2 and not game_over.value:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pygame.quit()
                is_quit = True
                game_over.value = True
                break

            if OPPONENT_MOVES:
                opponent_row, opponent_col = OPPONENT_MOVES.pop(0)
                current_game.matrix[opponent_row][opponent_col] = 2

                if current_game.is_game_over(2):
                    label = current_game.font.render("YOU LOST!!", True, Color.yellow)
                    current_game.screen.blit(label, (40, 10))
                    game_over.value = True

                turn = 1
                current_game.display_matrix()
                pygame.display.update()

    if game_over.value and not is_quit:
        time.sleep(5)
        pygame.quit()


def handle_msg(package: dict):
    """Handles the incoming packet"""
    pkg_type = package["TYPE"]
    if pkg_type == "RESPOND":
        incoming_respond(package)
    elif pkg_type == "DISCOVER":
        incoming_discovery(package)
    elif pkg_type == "MESSAGE":
        incoming_message(package)
    elif pkg_type == "GOODBYE":
        incoming_goodbye(package)
    elif pkg_type == "GAME":
        if package["INVITATION"]:
            incoming_game_invitation(package)
        else:
            incoming_game_response(package)
    elif pkg_type == "COORDINATION":
        incoming_coordinates(package)


def redefine_names(*args):
    """Redefines the value of "name" key of the packets"""
    for package in args:
        package["NAME"] = MY_NAME


def game_helper(opp_name, opp_ip, my_name, turn, game_chat, game_over):
    """Helper function for game operation"""
    global GAME_STATUS
    GAME_STATUS = True

    helper_thread = threading.Thread(target=helper_server_TCP, args=(game_chat,))
    helper_thread.start()

    chat_process = Process(target=chat_page, args=(opp_name, my_name, opp_ip, 100, 400, game_chat, game_over,))
    chat_process.start()

    game_page(opp_name, turn, game_over)
    GAME_STATUS = False
    chat_process.terminate()
    helper_thread.join()


if __name__ == "__main__":
    manager = Manager()
    game_chat = manager.list()
    MY_NAME = fe.login_page()
    game_over = Value("i", True)
    while MY_NAME == "":
        fe.popup_ok('Oops!', 'Message:', "User name cannot be blank, please enter a valid user name!")
        MY_NAME = fe.login_page()

    redefine_names(respond_package, goodbye_package, message_package, discovery_package, coordination_package,
                   game_package)
    server_thread = threading.Thread(target=runner_server_TCP)
    discovery_thread = threading.Thread(target=runner_server_UDP)
    send_discovery()
    server_thread.start()
    discovery_thread.start()
    invitation_send: str = ""
    time.sleep(0.5)  # incase respond did not came before showing the waiting room
    while True:
        home_window = fe.home_page(list(USERNAME_IP.keys()), invitation_send)
        home_event, home_values = home_window.read()
        invitation_send = ""

        if home_event == 'Accepted Game Response':
            fe.popup_ok('Game is calling :)',
                        "{0} has accepted your invitation".format(home_values['Accepted Game Response']),
                        "Press Okay to start the game now or wait few seconds:)")
            home_window.close()
            opponent_ip = USERNAME_IP[home_values['Accepted Game Response']]
            game_helper(home_values['Accepted Game Response'], opponent_ip, MY_NAME, 1, game_chat, game_over)

        elif home_event == 'Declined Game Response':
            fe.popup_ok('Sorry :(', "{0} is not available now.".format(home_values['Declined Game Response']),
                        "Don't give up, try to catch other players!")

        elif home_event == 'Incoming Game Invitation':  # Received a game invitation
            opponent_name = home_values['Incoming Game Invitation']
            my_response = fe.incoming_invitation_popup(opponent_name)
            game_package["INVITATION"] = False
            game_package["RESPOND"] = my_response
            send_package_TCP(opponent_name, game_package)
            if my_response:
                home_window.close()
                opponent_ip = USERNAME_IP[opponent_name]
                game_helper(opponent_name, opponent_ip, MY_NAME, 2, game_chat, game_over)

        elif home_event == 'Play':  # Pressed button Play
            if home_values["LB"]:
                send_game_invitation(home_values["LB"][0])
                invitation_send = "Game invitation is sent to {0}.".format(home_values["LB"][0])
            else:
                fe.popup_ok('Oops!', 'Message:', "Please select a user to play with!")

        elif home_event == "Chat":  # Pressed button Chat
            if home_values["LB"]:
                chat_page(home_values["LB"][0], MY_NAME)
            else:
                fe.popup_ok('Oops!', 'Message:', "Please select a user to chat with!")

        elif home_event == "Incoming Chat":  # Received a chat notification
            chat_values = home_values["Incoming Chat"]
            open_chat = fe.popup_chat("Notification", "New message from {0}!".format(chat_values[0]),
                                      chat_values[1])
            if open_chat:
                chat_page(chat_values[0], MY_NAME)

        elif home_event == "Update":  # Pressed button Update
            send_discovery()

        elif home_event in (None, Sg.WIN_CLOSED, 'Quit'):
            PROGRAM_STATUS = False
            home_window.close()
            server_thread.join()
            discovery_thread.join()
            send_goodbye()
            sys.exit()

        elif home_event == "Goodbye":
            fe.popup_ok("Sad news :(", "We've lost a friend", "{0} has left the room".format(home_values["Goodbye"]))

        home_window.close()
