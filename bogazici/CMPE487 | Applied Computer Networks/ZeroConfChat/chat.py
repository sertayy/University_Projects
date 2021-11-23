import os
import sys
import select
import socket
import json
import multiprocessing
import logging
from multiprocessing import Manager
from typing import Dict, Tuple
from datetime import datetime


def send_response(response_str: str, host: str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, 12345))
            sock.sendall(response_str.encode("utf-8"))
        except (ConnectionRefusedError, PermissionError, OSError):
            pass


def listen_udp(resp_json: Dict[str, str], user_dict: Dict[str, str]):
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(('', 12345))
            s.setblocking(0)
            result = select.select([s], [], [])
            msg = result[0][0].recv(1024).decode("utf-8")
            msg_dict = json.loads(msg)
            user_name = msg_dict["NAME"]
            ip_adr = msg_dict["MY_IP"]
            if ip_adr not in user_dict.values() and msg_dict["TYPE"] == "DISCOVER":
                response_str = json.dumps(resp_json) + "\n"
                p_listen_helper = multiprocessing.Process(target=send_response,
                                                          args=(response_str, ip_adr,))
                p_listen_helper.start()
                p_listen_helper.join()
                user_dict[user_name] = ip_adr
                print(user_name + " is added to your address list!")
                print("Address list: {0}".format(user_dict.keys()))

            elif msg_dict["TYPE"] == "GOODBYE" and user_name in user_dict.keys():
                print(user_name + " is leaved the chat room.")
                del (user_dict[user_name])


def listen_tcp(resp_json: Dict[str, str], user_dict: Dict[str, str]):
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", 12345))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    msg = conn.recv(1024)
                    msg_str = msg.decode("utf-8")
                    msg_dict = json.loads(msg_str)
                    user_name = msg_dict["NAME"]
                    ip_adr = addr[0]

                    if ip_adr not in user_dict.values() and msg_dict["TYPE"] == "RESPOND":
                        user_dict[user_name] = ip_adr
                        print(user_name + " is added to your address list!")
                        print("Address list: {0}".format(user_dict.keys()))

                    elif msg_dict["TYPE"] == "MESSAGE" and ip_adr in user_dict.values():
                        with open('chat_history.txt', "a") as f:
                            recv_msg = msg_dict["PAYLOAD"]
                            f.write("FROM {0} to {1}: \"{2}\" at {3}\n".format(user_name, resp_json["NAME"], recv_msg,
                                                                               datetime.now().strftime(
                                                                                   "%Y-%m-%d %H:%M:%S")))
                    elif msg_dict["TYPE"] == "MESSAGE" and ip_adr not in user_dict.values():
                        print("{0} is not in the address list. The message is hidden from the user!".format(ip_adr))
                    else:
                        logging.error("Something strange happened!")
            except OSError:
                pass


def send_goodbye(bye_dict: Dict[str, str]):
    bye_str = json.dumps(bye_dict) + "\n"
    msg_size = sys.getsizeof(bye_str)
    if msg_size < 1000:
        for i in range(3):
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                bye_str = json.dumps(bye_dict) + "\n"
                sock.bind(('', 0))
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(bye_str.encode("utf-8"), ('<broadcast>', 12345))
    else:
        logging.error("JSON content of UDP messages must be kept below 1000 bytes in size.")


def send_discover(disc_dict: Dict[str, str]):
    disc_str = json.dumps(disc_dict) + "\n"
    msg_size = sys.getsizeof(disc_str)
    if msg_size < 1000:
        for i in range(3):
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.bind(('', 0))
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(disc_str.encode("utf-8"), ('<broadcast>', 12345))
    else:
        logging.error("JSON content of UDP messages must be kept below 1000 bytes in size.")


def send_message(addr: str, message_str: str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((addr, 12345))
        message_str += "\n"
        s.sendall(message_str.encode("utf-8"))


def create_jsons() -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str], Dict[str, str]]:
    name = os.popen("whoami").read()[:-1]
    my_ip = os.popen("ipconfig getifaddr en0").read()[:-1]
    discover_dict = {
        "NAME": name,
        "MY_IP": my_ip,
        "TYPE": "DISCOVER",
        "PAYLOAD": ""
    }
    respond_dict = {
        "NAME": name,
        "MY_IP": my_ip,
        "TYPE": "RESPOND",
        "PAYLOAD": ""
    }
    message_dict = {
        "NAME": name,
        "MY_IP": my_ip,
        "TYPE": "MESSAGE",
        "PAYLOAD": ""
    }

    goodbye_dict = {
        "NAME": name,
        "MY_IP": my_ip,
        "TYPE": "GOODBYE",
        "PAYLOAD": "I am leaving."
    }

    return discover_dict, respond_dict, message_dict, goodbye_dict


if __name__ == '__main__':
    if os.path.exists("chat_history.txt"):
        os.remove("chat_history.txt")
    print("Welcome to Zeroconf Chat!")
    disc_json, resp_json, msg_json, bye_json = create_jsons()

    manager = Manager()
    user_dict = manager.dict()
    p_listen_udp = multiprocessing.Process(target=listen_udp, args=(resp_json, user_dict,))
    p_listen_udp.start()
    p_listen_tcp = multiprocessing.Process(target=listen_tcp, args=(resp_json, user_dict,))
    p_listen_tcp.start()
    p_discover = multiprocessing.Process(target=send_discover, args=(disc_json,))
    p_discover.start()

    while True:
        print("Address list: " + str(user_dict.keys()))
        user_name = input("Select a user name from the address list to chat.\n(You can quit anytime by entering 'exit' "
                          "command.)\n")
        if user_name in user_dict.keys():
            message_to_sent = input("USERNAME FOUND!\nWrite your message to {0}: ".format(user_name))
            msg_json["PAYLOAD"] = message_to_sent
            msg_str = json.dumps(msg_json) + "\n"
            try:
                user_adr = user_dict[user_name]
                send_message(user_adr, msg_str)
                with open('chat_history.txt', "a+") as f:
                    f.write("FROM {0} to {1}: \"{2}\" at {3}\n".format(msg_json["NAME"], user_name, message_to_sent,
                                                                       datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            except KeyError:
                logging.error("WARNING! Unexpected offline client detected.")
            except (ConnectionRefusedError, PermissionError, OSError) as ex:
                logging.error(ex)

        elif user_name == "exit":
            send_goodbye(bye_json)
            p_listen_udp.terminate()
            p_listen_tcp.terminate()
            sys.exit()
        else:
            logging.error("{0} is not in the address list. Please select an available user.".format(user_name))
