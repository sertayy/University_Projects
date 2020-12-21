import socket
import multiprocessing
import logging
import os
from typing import Dict, Tuple
from multiprocessing import Manager
import json
from datetime import datetime


def listen(resp_json: Dict[str, str], user_dict: Dict[str, str]):
    HOST = ""
    PORT = 12345
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((HOST, PORT))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print("Connected by", addr[0])
                    data = conn.recv(1024)
                    data_str = data.decode("utf-8")
                    data_dict = json.loads(data_str)
                    user_name = data_dict["NAME"]
                    ip_adr = addr[0]
                    if ip_adr not in list(user_dict.values()):
                        if data_dict["TYPE"] == "DISCOVER":
                            response_str = json.dumps(resp_json) + "\n"
                            p_listen_helper = multiprocessing.Process(target=send_response, args=(response_str, ip_adr,))
                            p_listen_helper.start()
                            p_listen_helper.join()
                            user_dict[user_name] = ip_adr
                            print(user_name + " is added to your address list!")
                            print("Address list: " + str(user_dict.keys()))

                        elif data_dict["TYPE"] == "RESPOND":
                            user_dict[user_name] = ip_adr
                            print(user_name + " is added to your address list!")
                            print("Address list: " + str(user_dict.keys()))

                    elif data_dict["TYPE"] == "MESSAGE" and ip_adr in list(user_dict.values()):
                        with open('chat_history.txt', "a") as f:
                            recv_msg = data_dict["PAYLOAD"]
                            f.write("FROM {0} to {1}: \"{2}\" at {3}\n".format(user_name, resp_json["NAME"], recv_msg,
                                                                               datetime.now().strftime(
                                                                                   "%Y-%m-%d %H:%M:%S")))
                    elif data_dict["TYPE"] == "MESSAGE" and ip_adr not in list(user_dict.values()):
                        print("{0} is not in the address list. The message is hidden from the user!".format(ip_adr))
                    else:
                        logging.error("Something strange happened!")
            except OSError:
                pass


def get_response(resp_json: Dict[str, str], user_dict: Dict[str, str]):
        p_get_response = multiprocessing.Process(target=listen, args=(resp_json, user_dict,))
        p_get_response.start()


def discover_ip(disc_dict: Dict):
    my_ip = int(disc_dict["MY_IP"][-3:])
    common_ip = disc_dict["MY_IP"][:-3]
    discover_str = json.dumps(disc_dict) + "\n"
    for ip_num in range(0, 255):
        if ip_num != my_ip:
            ip_adr = common_ip + str(ip_num)
            p1 = multiprocessing.Process(target=send_discover, args=(discover_str, ip_adr,))
            p1.start()


def send_discover(discover_str: str, HOST: str):
    PORT = 12345
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            s.sendall(discover_str.encode("utf-8"))
        except (ConnectionRefusedError, PermissionError, OSError):
            pass


def send_response(response_str: str, HOST: str):
    PORT = 12345
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            s.sendall(response_str.encode("utf-8"))
        except (ConnectionRefusedError, PermissionError, OSError):
            pass


def send_message(addr: str, message_str: str):
    PORT = 12345
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((addr, PORT))
        message_str += "\n"
        s.sendall(message_str.encode("utf-8"))


def simulation(disc_json: Dict[str, str], resp_json: Dict[str, str], user_dict: Dict[str, str]):
    p_listen = multiprocessing.Process(target=get_response, args=(resp_json, user_dict,))
    p_listen.start()
    p_discover = multiprocessing.Process(target=discover_ip, args=(disc_json,))
    p_discover.start()


def create_jsons() -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
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
    return discover_dict, respond_dict, message_dict


if __name__ == '__main__':
    if os.path.exists("chat_history.txt"):
        os.remove("chat_history.txt")
    print("Welcome to BuChat!")
    disc_json, resp_json, msg_json = create_jsons()
    manager = Manager()
    user_dict = manager.dict()
    p_simulate = multiprocessing.Process(target=simulation, args=(disc_json, resp_json, user_dict,))
    p_simulate.start()
    common_ip: str = msg_json["MY_IP"][:-3]
    port = 12345

    while True:
        print("Address list: " + str(user_dict.keys()))
        user_name = input("Select a user name from the address list: \n")
        if user_name in user_dict.keys():
            message_to_sent = input("USERNAME FOUND!\nWrite your message to {0}: ".format(user_name))
            msg_json["PAYLOAD"] = message_to_sent
            msg_str = json.dumps(msg_json) + "\n"
            user_adr = user_dict[user_name]
            try:
                send_message(user_adr, msg_str)
                with open('chat_history.txt', "a+") as f:
                    f.write("FROM {0} to {1}: \"{2}\" at {3}\n".format(msg_json["NAME"], user_name, message_to_sent,
                                                                   datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            except (ConnectionRefusedError, PermissionError, OSError) as ex:
                logging.error("{0} | host ---> {1}".format(ex, user_adr))
        else:
            logging.error("{0} is not in the user dict! IP NOT FOUND!".format(user_name))
