import json
import os
import subprocess
import multiprocessing
from datetime import datetime
from multiprocessing import Manager
from typing import Dict, Tuple
import logging


def send_disc(packet, nc_command):
    echo_command = "echo " + "\"" + packet + "\"" + " | " + nc_command
    os.system(echo_command)


def send_resp(packet, nc_cmd):
    echo_cmd = "echo " + "\"" + packet + "\"" + " | " + nc_cmd
    os.system(echo_cmd)


def listen(nc_command):
    os.system(nc_command)


def get_name_and_ip(response_str) -> Tuple[str, str]:
    start = response_str.find("NAME") + 6
    finish = response_str.find("MY_IP") - 2
    name = response_str[start:finish]
    start = response_str.find("MY_IP") + 7
    finish = response_str.find("TYPE") - 2
    ip = response_str[start:finish]
    return name, ip


def get_response(resp_dict, user_dict):
    port: str = "12345"
    resp_packet = str(json.dumps(resp_dict))
    while True:
        server = subprocess.run(["nc", "-l", port], stdout=subprocess.PIPE)
        response_str = str(server.stdout)
        if response_str != "":
            user_name, user_ip = get_name_and_ip(response_str)
            nc_command: str = "nc -vn -w 1 " + user_ip + " " + port
            initial_type = response_str.find("TYPE") + 6
            if user_ip not in list(user_dict.values()):
                user_dict[user_name] = user_ip
                print(user_name + " is added to your address list!")
                print("Address list: " + str(user_dict.keys()))
                print("Select a user name from the address list: ")
                if response_str[initial_type:initial_type + 1] == "D":
                    p_response = multiprocessing.Process(target=send_resp, args=(resp_packet, nc_command,))
                    p_response.start()
            elif response_str[initial_type: initial_type + 1] == "M" and user_ip in list(user_dict.values()):
                with open('chat_history.txt', "a") as f:
                    initial_m = response_str.find("PAYLOAD") + 9
                    last_m = response_str.rfind("}")
                    recv_msg = response_str[initial_m:last_m]
                    f.write("FROM {0} to {1}: \"{2}\" at {3}\n".format(user_name, resp_dict["NAME"], recv_msg,
                                                                       datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            elif response_str[initial_type: initial_type + 1] == "M" and user_ip not in list(user_dict.values()):
                print("{0} is not in the address list. The message is hidden from the user!".format(user_ip))
            else:
                logging.error("Something wrong happened!")


def discover_ip(disc_dict):
    common_ip: str = disc_dict["MY_IP"][:-3]
    my_ip = int(disc_dict["MY_IP"][-3:])
    port: str = "12345"
    packet = str(json.dumps(disc_dict))
    for i in range(254, 255):
        if i != my_ip:
            nc_command: str = "nc -vn -w 1 " + common_ip + str(i) + " " + port
            p1 = multiprocessing.Process(target=send_disc, args=(packet, nc_command,))
            p1.start()


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


def simulation(disc_json, resp_json, user_dict):
    p_discover = multiprocessing.Process(target=discover_ip, args=(disc_json,))
    p_discover.start()

    while True:
        p2 = multiprocessing.Process(target=get_response, args=(resp_json, user_dict,))
        p2.start()
        p2.join()
        print(1)


if __name__ == '__main__':
    if os.path.exists("chat_history.txt"):
        os.remove("chat_history.txt")

    print("Welcome to BuChat!")
    disc_json, resp_json, msg_json = create_jsons()
    manager = Manager()
    user_dict = manager.dict()
    p_simulate = multiprocessing.Process(target=simulation, args=(disc_json, resp_json, user_dict,))
    p_simulate.start()
    while True:
        print("Address list: " + str(user_dict.keys()))
        user_name = input("Select a user name from the address list: \n")
        if user_name in user_dict.keys():
            message_to_sent = input("USERNAME FOUND!\nWrite your message to {0}: ".format(user_name))
            msg_json["PAYLOAD"] = message_to_sent
            msg_packet = str(json.dumps(msg_json))
            common_ip: str = msg_json["MY_IP"][:-3]
            port = "12345"
            nc_command: str = "nc -vn -w 1 " + user_dict[user_name] + " " + port
            echo_command = "echo " + "\"" + msg_packet + "\"" + " | " + nc_command
            os.system(echo_command)
            with open('chat_history.txt', "a+") as f:
                f.write("FROM {0} to {1}: \"{2}\" at {3}\n".format(msg_json["NAME"], user_name, message_to_sent,
                                                                   datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        else:
            logging.info("{0} is not in the user dict! IP NOT FOUND!".format(user_name))
