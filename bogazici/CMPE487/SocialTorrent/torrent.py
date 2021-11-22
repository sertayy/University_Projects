import os
import sys
import select
import socket
import multiprocessing
import logging
from multiprocessing import Manager
from typing import Dict, List
from datetime import datetime
import time
import pickle

MAX_BUFFER_SIZE: int = 1.5 * (10 ** 6)
PORT_DEFAULT = 12345
PORT_ACK = 12346
PORT_TORRENT = 12347


def send_response(response_str: bytes, host: str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, PORT_DEFAULT))
            sock.sendall(response_str)
        except (ConnectionRefusedError, PermissionError, OSError):
            pass


def listen_ack(current_serial):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(('', PORT_ACK))
            s.settimeout(1)
            result = select.select([s], [], [])
            msg = result[0][0].recv(1500)
            s.close()
            msg_dict = pickle.loads(msg)
            serial = msg_dict["SERIAL"]

            if serial != current_serial:
                return -1
            if msg_dict["TYPE"] == "ACK":
                buffer_space_left = msg_dict["rwnd"]
                return buffer_space_left
    except Exception as ex:
        logging.error("Something wrong happened while listening acknowledge. --> {0}".format(ex))
        return None


def send_ack(ack_dict, serial_num, ip_adr, buffer):
    buffer_size = 0
    for data in buffer:
        buffer_size += sys.getsizeof(data)
    current_buffer_size = MAX_BUFFER_SIZE - buffer_size

    ack_dict["rwnd"] = current_buffer_size
    ack_dict["SERIAL"] = serial_num
    acknowledge_str = pickle.dumps(ack_dict) + "\n".encode("utf-8")
    for i in range(10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.bind(('', 0))
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(acknowledge_str, (ip_adr, PORT_ACK))
        except Exception as ex:
            logging.error("Something wrong happened while sending acknowledge. --> {0}".format(ex))


def listen_tcp(resp_json, user_dict, file_dict, msg_to_send, my_files, buffer, network_torrent_files, ack_dict, my_torrent_files):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", PORT_DEFAULT))
            s.listen()
            conn, addr = s.accept()
            s.close()
            with conn:
                msg = conn.recv(1500)
                incoming_msg_dict = pickle.loads(msg)
                user_name = incoming_msg_dict["NAME"]
                ip_adr = addr[0]
                if ip_adr not in user_dict.values() and incoming_msg_dict["TYPE"] == "RESPOND":
                    user_dict[user_name] = ip_adr
                    print(user_name + " is added to your address list!")
                    print("Address list: {0}".format(user_dict.keys()))

                elif incoming_msg_dict["TYPE"] == "RESPOND" and incoming_msg_dict["PAYLOAD"] != "":
                    incoming_list = incoming_msg_dict["PAYLOAD"]
                    for file_serial in incoming_list:
                        network_torrent_files[file_serial] = ip_adr

                elif ip_adr in user_dict.values() and incoming_msg_dict["TYPE"] == "MESSAGE":
                    if incoming_msg_dict["APPROVE_FILE"]:  # göndermek istiyoruz
                        print("We are sending the file {0}".format(incoming_msg_dict["PAYLOAD"]))
                        send_file(file_dict, msg_to_send, user_name, incoming_msg_dict["PAYLOAD"],
                                  incoming_msg_dict["MY_IP"])

                    elif incoming_msg_dict["REQUEST_ACK"]:
                        send_ack(ack_dict, incoming_msg_dict["PAYLOAD"], incoming_msg_dict["MY_IP"],buffer)

                    elif incoming_msg_dict["REQUEST_DOWNLOAD"]: # yaziyoz
                        send_chunk(incoming_msg_dict["PAYLOAD"], incoming_msg_dict["MY_IP"], file_dict, my_torrent_files)

                    elif incoming_msg_dict["IS_FILE"]:  # o gönderecek, biz alıcaz
                        print("We are downloading the file {0} ...".format(incoming_msg_dict["PAYLOAD"]))
                        msg_to_send["APPROVE_FILE"] = True
                        msg_to_send["PAYLOAD"] = incoming_msg_dict["PAYLOAD"]
                        send_message(user_dict[user_name], pickle.dumps(msg_to_send))


                    elif incoming_msg_dict["CORRUPTED_FILE"]:
                        file_name = incoming_msg_dict["PAYLOAD"]
                        keys: List[str] = list(my_files.keys())
                        for key in keys:
                            if key.startswith(file_name):
                                buffer.remove(my_files[key])
                                del my_files[key]

                    elif incoming_msg_dict["DONE_FILE"]:
                        create_file(incoming_msg_dict, my_files, buffer)
                        pass

                    elif ip_adr in user_dict.values():  # NORMAL CHAT
                        with open('chat_history.txt', "a") as f:
                            recv_msg = incoming_msg_dict["PAYLOAD"]
                            print("{0}: {1}".format(user_name, incoming_msg_dict["PAYLOAD"]))
                            f.write(
                                "FROM {0} to {1}: \"{2}\" at {3}\n".format(user_name, resp_json["NAME"], recv_msg,
                                                                           datetime.now().strftime(
                                                                               "%Y-%m-%d %H:%M:%S")))
                    else:
                        logging.error("Something strange happened! in message type (listentcp)")
                elif incoming_msg_dict["TYPE"] == "MESSAGE" and ip_adr not in user_dict.values():
                    print("{0} is not in the address list. The message is hidden from the user!".format(ip_adr))
                else:
                    logging.error("Something strange happened!")
        except OSError:
            pass


def listen_udp(resp_json, user_dict, ack_dict, my_files, buffer, my_torrent_files):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(('', PORT_DEFAULT))
            s.setblocking(0)
            result = select.select([s], [], [])
            msg = result[0][0].recv(1500)
            s.close()
            incoming_msg_dict = pickle.loads(msg)
            ip_adr = incoming_msg_dict["MY_IP"]

            if ip_adr not in user_dict.values() and incoming_msg_dict["TYPE"] == "DISCOVER":
                user_name = incoming_msg_dict["NAME"]
                response_str = pickle.dumps(resp_json) + "\n".encode("utf-8")
                p_listen_helper = multiprocessing.Process(target=send_response, args=(response_str, ip_adr,))
                p_listen_helper.start()
                p_listen_helper.join()
                user_dict[user_name] = ip_adr
                print(user_name + " is added to your address list!")
                print("Address list: {0}".format(user_dict.keys()))

            elif incoming_msg_dict["TYPE"] == "DISCOVER" and incoming_msg_dict["UPLOAD_ERR"]:
                keys = my_torrent_files.keys()
                for key in keys:
                    if key.startswith(incoming_msg_dict["PAYLOAD"]):
                        buffer.remove(my_torrent_files[key])
                        del my_torrent_files[key]

            elif ip_adr in user_dict.values() and incoming_msg_dict["TYPE"] == "DISCOVER" and incoming_msg_dict["IS_TORRENT"]:
                user_name = incoming_msg_dict["NAME"]
                resp_json["PAYLOAD"] = list(my_torrent_files.keys())
                response_str = pickle.dumps(resp_json) + "\n".encode("utf-8")
                p_listen_helper = multiprocessing.Process(target=send_response, args=(response_str, ip_adr,))
                p_listen_helper.start()
                p_listen_helper.join()

            elif incoming_msg_dict["TYPE"] == "GOODBYE" and incoming_msg_dict["NAME"] in user_dict.keys():
                print(incoming_msg_dict["NAME"] + " is leaved the chat room.")
                del (user_dict[incoming_msg_dict["NAME"]])

            elif incoming_msg_dict["TYPE"] == "FILE":
                read_incoming_file(incoming_msg_dict, my_files, buffer, my_torrent_files)
                if not incoming_msg_dict["IS_TORRENT"]:
                    print("incoming serial {0}".format(incoming_msg_dict["SERIAL"]))
                    send_ack(ack_dict, incoming_msg_dict["SERIAL"], ip_adr, buffer)
            else:
                logging.error("We have received an unknown packet!!!")
        except Exception as ex:
            logging.error("Something wrong happened in listen_udp. --> {0}".format(ex))


def create_file(msg_packet, my_files, buffer):
    file_name: str = msg_packet["PAYLOAD"]
    file_name = file_name[:file_name.rfind("_")]
    keys: List[str] = list(my_files.keys())
    with open(file_name, "wb") as out_file:
        for key in keys:
            if key.startswith(file_name):
                out_file.write(my_files[key])
                if my_files[key] in buffer:
                    buffer.remove(my_files[key])

    print("{0} is downloaded and created :)".format(file_name))


def send_chunk(file_serial, ip_addr, file_dict, my_torrent_files):

    file_dict["PAYLOAD"] = my_torrent_files[file_serial]
    file_dict["FILE_NAME"] = file_serial[:file_serial.rfind("_")]
    file_dict["SERIAL"] = int(file_serial[file_serial.rfind("_")+1:])
    file_dict["IS_TORRENT"] = True

    for i in range(10):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('', 0))
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(pickle.dumps(file_dict), (ip_addr, PORT_TORRENT))


def recieve_chunk(serial):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(('', PORT_TORRENT))
            s.settimeout(1)
            result = select.select([s], [], [])
            msg = result[0][0].recv(1500)
            s.close()
            data = pickle.loads(msg)    
            current_serial = data["SERIAL"]  
            if current_serial != serial:
                print("torrent yanlis gelen serial {0}".format(current_serial))
                print("torrent parametre {0}".format(serial))
                return -1
            else:
                return data["PAYLOAD"]
           
    except Exception as ex:
        logging.error("Something wrong happened while receiving chunk. --> {0}".format(ex))
        return None


def download_file(file_name, network_torrent_files, msg_dict, my_torrent_files):
    print("{0} is downloading via torrent...".format(file_name))
    download_dict = []
    downloaded_data_list = []

    for file_serial in network_torrent_files.keys():
        if file_serial.startswith(file_name):
            serial = int(file_serial[file_serial.rfind("_")+1:])
            download_dict.append((serial, network_torrent_files[file_serial]))

    for file_serial in my_torrent_files.keys():
        if file_serial.startswith(file_name):
            serial = int(file_serial[file_serial.rfind("_")+1:])
            download_dict.append((serial, 0))
    download_dict = sorted(download_dict, key=lambda x: x[0])

    for tup in download_dict: 
        msg_dict["REQUEST_DOWNLOAD"] = True
        msg_dict["PAYLOAD"] = file_name + "_" + str(tup[0])

        if tup[1] == 0:
            received_data = my_torrent_files[msg_dict["PAYLOAD"]]
        else:
            send_message(tup[1], pickle.dumps(msg_dict))
            received_data = recieve_chunk(tup[0])
            counter = 0
            while received_data == -1:
                send_message(tup[1], pickle.dumps(msg_dict))
                time.sleep(0.1)
                received_data = recieve_chunk(tup[0])
                counter += 1
                if counter == 100:
                    print("Can not downloaded.")
                    break

        buffer.append(received_data)
        downloaded_data_list.append(received_data)
    with open(file_name, "wb") as file:
        for data in downloaded_data_list:
            file.write(data)
            if data in buffer:
                buffer.remove(data)

    print("{0} has downloaded via torrent :)".format(file_name))


def read_incoming_file(file_packet, my_files, buffer, my_torrent_files):
    data = file_packet["PAYLOAD"]
    serial = file_packet["SERIAL"]
    file_name = file_packet["FILE_NAME"]
    if data != b"":
        if not file_packet["IS_TORRENT"]:
            my_files[file_name + "_" + str(serial)] = data  # global variable
            buffer.append(data)  
        else:
            my_torrent_files[file_name + "_" + str(serial)] = data  # global
            buffer.append(data)  # buffer, şimdilik

    else:  # buraya bak
        buffer[:] = []


def send_goodbye(bye_dict: Dict[str, str]):
    bye_str = pickle.dumps(bye_dict) + "\n".encode("utf-8")
    msg_size = sys.getsizeof(bye_str)
    if msg_size < 1000:
        for i in range(3):
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.bind(('', 0))
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(bye_str, ("25.255.255.255", PORT_DEFAULT))
    else:
        logging.error("JSON content of UDP messages must be kept below 1000 bytes in size.")


def send_discover(disc_dict):
    disc_str = pickle.dumps(disc_dict) + "\n".encode("utf-8")
    msg_size = sys.getsizeof(disc_str)
    if msg_size < 1000:
        for i in range(3):
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.bind(('', 0))
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(disc_str, ("25.255.255.255", PORT_DEFAULT))
    else:
        logging.error("JSON content of UDP messages must be kept below 1000 bytes in size.")


def send_message(addr: str, message_str: bytes):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((addr, PORT_DEFAULT))
        message_str += "\n".encode("utf-8")
        s.sendall(message_str)


def send_file(file_packet, msg_packet, user_name, file_name, ip_address):
    file_packet["FILE_NAME"] = file_name
    file_packet_str = pickle.dumps(file_packet)
    packet_size = sys.getsizeof(file_packet_str)
    counter = 0
    with open(file_name, "rb") as file:
        data = file.read(1400 - packet_size)
        file_packet["PAYLOAD"] = data
        file_packet_str = pickle.dumps(file_packet)
        packet_size = sys.getsizeof(file_packet_str)
        while data:

            if packet_size <= 1500:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.bind(('', 0))
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.sendto(file_packet_str, (ip_address, PORT_DEFAULT))
                    sock.close()
                    if counter < 2:
                        space_left = listen_ack(file_packet["SERIAL"])

                        while space_left == -1:
                            space_left = listen_ack(file_packet["SERIAL"])
                            
                        if space_left is None:
                            counter += 1
                            continue
                        if space_left > 10 ** 6:  # 1 mb olcak
                            file_packet["SERIAL"] += 1
                            file_packet["PAYLOAD"] = ""
                            file_packet_str = pickle.dumps(file_packet)
                            data = file.read(1400 - sys.getsizeof(file_packet_str))
                            file_packet["PAYLOAD"] = data
                            file_packet_str = pickle.dumps(file_packet)
                            packet_size = sys.getsizeof(file_packet_str)
                        else:
                            file_packet["PAYLOAD"] = ""
                            file_packet_str = pickle.dumps(file_packet)
                            packet_size = sys.getsizeof(file_packet_str)
                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            sock.bind(('', 0))
                            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                            sock.sendto(file_packet_str, (ip_address, PORT_DEFAULT))
                            sock.close()
                            time.sleep(60)  # 1 dk olcak
                    else:
                        logging.error("lost packet with serial {0}".format(file_packet["SERIAL"]))
                        msg_packet["CORRUPTED_FILE"] = True
                        msg_packet["PAYLOAD"] = file_name
                        send_message(ip_address, pickle.dumps(msg_packet))
                        break
                except Exception as ex:
                    logging.error("Error happened in send file ---> {0}".format(ex))
            else:
                logging.error("JSON content of file packets must be kept below 1500 bytes in size.")
                break

        if data == b"":
            print("{0} file has sent".format(file_name))
            msg_packet["DONE_FILE"] = True
            msg_packet["PAYLOAD"] = file_name + "_" + str(file_packet["SERIAL"] - 1)
            send_message(ip_address, pickle.dumps(msg_packet))


def upload_file(user_dict, file_json, msg_json, disc_json):
    file_packet_str = pickle.dumps(file_json)
    packet_size = sys.getsizeof(file_packet_str)
    file_name = file_json["FILE_NAME"]
    file_json["IS_TORRENT"] = True
    with open("my_files/" + file_name, "rb") as file:
        data = file.read(1400 - packet_size)
        file_json["PAYLOAD"] = data
        file_packet_str = pickle.dumps(file_json)
        packet_size = sys.getsizeof(file_packet_str)
        counter = 0
        index = 0
        while data:
            index += 1
            if index > len(user_dict.keys()):
                index = index % (len(user_dict.keys()))
            msg_json["REQUEST_ACK"] = True
            msg_json["PAYLOAD"] = file_json["SERIAL"]
            user_names = list(user_dict.keys())
            send_message(user_dict[user_names[index-1]], pickle.dumps(msg_json))
            space_left = listen_ack(file_json["SERIAL"])
            counter = 0
            while space_left == -1:
                send_message(user_dict[user_names[index-1]], pickle.dumps(msg_json))
                time.sleep(0.1)
                space_left = listen_ack(file_json["SERIAL"])
                counter += 1
                if counter == 100:
                    print("Can not uploaded.")
                    break
            if packet_size <= 1500:
                if counter < 3:
                    if space_left is None:
                        counter += 1
                        continue
                    if space_left > 10**6:
                        try:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            sock.bind(('', 0))
                            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                            sock.sendto(file_packet_str, (user_dict[user_names[index-1]], PORT_DEFAULT))
                            sock.close()
                            file_json["SERIAL"] += 1
                            file_json["PAYLOAD"] = ""
                            file_packet_str = pickle.dumps(file_json)
                            data = file.read(1400 - sys.getsizeof(file_packet_str))
                            file_json["PAYLOAD"] = data
                            file_packet_str = pickle.dumps(file_json)
                            packet_size = sys.getsizeof(file_packet_str)
                        except Exception as ex:
                            logging.error("Error happened in upload file/spaceleft ---> {0}".format(ex))

                    else:
                        try:
                            file_json["PAYLOAD"] = ""
                            file_packet_str = pickle.dumps(file_json)
                            packet_size = sys.getsizeof(file_packet_str)
                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            sock.bind(('', 0))
                            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                            sock.sendto(file_packet_str, (user_dict[user_names[index-1]], PORT_DEFAULT))
                            sock.close()
                            time.sleep(60)  # 1 dk olcak
                        except Exception as ex:
                            logging.error("Error happened in upload file/no spaceleft ---> {0}".format(ex))
                else:
                    logging.error("lost packet with serial {0}".format(file_json["SERIAL"]))
                    disc_json["UPLOAD_ERR"] = True
                    disc_json["PAYLOAD"] = file_name
                    send_discover(disc_json)
                    break
            else:
                logging.error("JSON content of file packets must be kept below 1500 bytes in size.")
                break
        if data == b"":
            print("{0} file has uploaded to torrent".format(file_name))


def create_jsons():
    name = os.popen("whoami").read()[:-1]
    # my_ip = os.popen("ipconfig getifaddr en0").read()[:-1]
    my_ip = "25.71.242.16"

    discover_dict = {
        "NAME": name,
        "MY_IP": my_ip,
        "TYPE": "DISCOVER",
        "PAYLOAD": "",
        "IS_TORRENT": False,
        "UPLOAD_ERR": False
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
        "PAYLOAD": "",
        "APPROVE_FILE": False,
        "DONE_FILE": False,
        "IS_FILE": False,
        "CORRUPTED_FILE": False,
        "REQUEST_ACK" : False,
        "REQUEST_DOWNLOAD" : False
    }

    goodbye_dict = {
        "NAME": name,
        "MY_IP": my_ip,
        "TYPE": "GOODBYE",
        "PAYLOAD": "I am leaving."
    }

    file_dict = {
        "TYPE": "FILE",
        "SERIAL": 0,
        "PAYLOAD": "",
        "FILE_NAME": "",
        "MY_IP": my_ip,
        "IS_TORRENT": False
    }

    ack_dict = {
        "TYPE": "ACK",
        "rwnd": "",
        "SERIAL": 0
    }

    return discover_dict, respond_dict, message_dict, goodbye_dict, file_dict, ack_dict


if __name__ == '__main__':
    if os.path.exists("chat_history.txt"):
        os.remove("chat_history.txt")
    print("Welcome to Zeroconf Chat!")
    disc_json, resp_json, msg_json, bye_json, file_json, ack_dict = create_jsons()

    manager = Manager()  # process'ler tarafından değiştirebilir global değişken
    user_dict = manager.dict()
    buffer: List = manager.list()
 
    my_torrent_files = manager.dict()  # {filename_serial : payload(bytes)}}
    network_torrent_files = manager.dict()  # {filename_serial : IP_addr}}
    my_files = manager.dict()  # {filename_serial : payload(bytes)}}
    p_listen_udp = multiprocessing.Process(target=listen_udp,
                                           args=(resp_json, user_dict, ack_dict, my_files, buffer, my_torrent_files,))
    p_listen_udp.start()
    p_listen_tcp = multiprocessing.Process(target=listen_tcp, args=(resp_json, user_dict, file_json, msg_json, my_files,
                                                                    buffer, network_torrent_files, 
                                                                    ack_dict, my_torrent_files, ))
    p_listen_tcp.start()
    p_discover = multiprocessing.Process(target=send_discover, args=(disc_json,))
    p_discover.start()
    local_files = os.listdir(os.path.join(os.getcwd(), "my_files"))
    uploaded_files = []

    while True:
        disc_json, resp_json, msg_json, bye_json, file_json, ack_dict = create_jsons()
        option = input("Chat, send file or torrent?\n")
        if option == "file":
            # if any person exist in the dict, if not continue;
            file_name = input("Which file?\n")
            # os.path.exists(os.path.curdir + "/o")

            # file_name exists?
            print("Address list: " + str(user_dict.keys()))
            user_name = input("Choose a person to send file.\n")
            if user_name in user_dict.keys():
                msg_json["PAYLOAD"] = file_name
                msg_json["IS_FILE"] = True
                send_message(user_dict[user_name], pickle.dumps(msg_json))
            else:
                logging.error("{0} is not in your dict.".format(user_name))
                continue
        elif option == "chat":
            print("Address list: " + str(user_dict.keys()))
            user_name = input("Select a user name from the address list to chat.\n(You can quit anytime by entering "
                              "'exit' command.)\n")
            if user_name in user_dict.keys():
                message_to_sent = input("USERNAME FOUND!\nWrite your message to {0}: ".format(user_name))
                msg_json["PAYLOAD"] = message_to_sent
                try:
                    user_adr = user_dict[user_name]
                    send_message(user_adr, pickle.dumps(msg_json))
                    with open('chat_history.txt', "a+") as f:
                        f.write("FROM {0} to {1}: \"{2}\" at {3}\n".format(msg_json["NAME"], user_name, message_to_sent,
                                                                           datetime.now().strftime(
                                                                               "%Y-%m-%d %H:%M:%S")))
                except KeyError:
                    logging.error("WARNING! Unexpected offline client detected.")
                except (ConnectionRefusedError, PermissionError, OSError) as ex:
                    logging.error(ex)

            elif user_name == "exit":
                send_goodbye(bye_json)
                p_listen_udp.terminate()
                sys.exit()
            else:
                logging.error("{0} is not in the address list. Please select an available user.".format(user_name))

        elif option == "torrent":
            option = input("Download or upload, please enter your option?\n")
            if option == "upload":
                for file_name in local_files:
                    if file_name not in uploaded_files:  # upload ettiğini bir daha upload lamamak için
                        option = input("Do you want upload this (Y/N) --> {0}\n".format(file_name))
                        if option == "Y":
                            uploaded_files.append(file_name)
                            file_json["FILE_NAME"] = file_name
                            upload_file(user_dict, file_json, msg_json, disc_json)
                            break
            elif option == "download":
                network_torrent_files.clear()
                disc_json["IS_TORRENT"] = True
                send_discover(disc_json)
                print("Getting all possible files...")
                time.sleep(1)

                file_names = []
                for file_serial in network_torrent_files.keys():
                    file = file_serial[:file_serial.rfind("_")]
                    if file not in file_names:
                        file_names.append(file)

                for file_serial in my_torrent_files.keys():
                    file = file_serial[:file_serial.rfind("_")]
                    if file not in file_names:
                        file_names.append(file)

                inp = input("Choose file from available files: {0}".format(file_names))
                download_file(inp, network_torrent_files, msg_json, my_torrent_files)







