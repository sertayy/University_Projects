import sys
from typing import List
import PySimpleGUI as Sg


def login_page() -> str:
    """Returns the user name"""
    layout = [[Sg.Text('Welcome to Online Connect Four Game!')],
              [Sg.Text('Enter your user name:'), Sg.InputText()],
              [Sg.Button('Enter'), Sg.Button('Quit')]]
    window = Sg.Window('Login Page', layout)
    while True:
        event, values = window.read()
        if event in (None, Sg.WIN_CLOSED, 'Quit'):
            sys.exit()
        elif event == 'Enter':
            name = values[0]
            break
    window.close()
    return name


def popup_ok(header: str, title: str, message: str):
    """Pop up with OK and auto close mode on"""
    layout = [[Sg.Text(title)],
              [Sg.Text(message)],
              [Sg.Button('Okay')]]  # identify the multiline via key option
    window = Sg.Window(header, layout, auto_close=True, auto_close_duration=5)
    while True:
        event, values = window.read()
        if event in (None, Sg.WIN_CLOSED):  # if user closes window or clicks Quit
            break
        elif event == 'Okay':
            break
    window.close()


def popup_chat(header: str, title: str, message: str):
    """Incoming chat pop up"""
    response = False
    layout = [[Sg.Text(title)],
              [Sg.Text(message)],
              [Sg.Button('See'), Sg.Button('Close')]]
    window = Sg.Window(header, layout, keep_on_top=True)
    while True:
        event, values = window.read()
        if event in (None, Sg.WIN_CLOSED):  # if user closes window or clicks Quit
            break
        elif event == 'See':
            response = True
            break
        elif event == 'Close':
            break

    window.close()
    return response


def incoming_invitation_popup(user_name: str) -> bool:
    """Incoming game invitation pop up"""
    response = False
    layout = [[Sg.Text("{0} has invited you to play a game!".format(user_name))],
              [Sg.Button('Accept'), Sg.Button('Decline')]]
    window = Sg.Window('Game is calling :)', layout).Finalize()
    while True:
        event, values = window.read(timeout=10000)
        print(event)
        if event in (None, Sg.WIN_CLOSED, 'Quit', "__TIMEOUT__"):  # if user closes window or clicks Quit
            break
        elif event == 'Accept':
            response = True
            break
        elif event == 'Decline':
            response = False
            break
    window.close()
    return response


def home_page(user_list: List[str], invitation_message: str):
    """Home page visual"""
    if user_list:
        text = "Choose a player to play with!"
    else:
        text = "There is no online player right now :("
    if invitation_message != "":
        layout = [[Sg.Text(text=text)], [Sg.Text(text=invitation_message)],
                  [Sg.Listbox(user_list, size=(20, 3), key='LB')], [Sg.Button('Play'), Sg.Button('Chat'),
                                                                    Sg.Button('Update'), Sg.Button('Quit')]]
    else:
        layout = [[Sg.Text(text=text)], [Sg.Listbox(user_list, size=(20, 3), key='LB')],
                  [Sg.Button('Play'), Sg.Button('Chat'), Sg.Button('Update'), Sg.Button('Quit')]]
    window = Sg.Window('Waiting Room', layout).finalize()
    return window
