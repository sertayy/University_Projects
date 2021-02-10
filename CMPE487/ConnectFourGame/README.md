# Online Connect Four Game
In this project, we have implemented an online Connect Four Game.

## Required packages
 | package | version |
 | ------- | ------- |
 | Numpy   | 1.20.0  |
 | Pygame  | 2.0.1  |
 | PySimpleGUI  | 4.34.0  |

##  Execution
To run the program, execute the following from terminal, inside the project folder:
```
python3 main.py
```
You'll be directed to the login page. After entering your username, the home page (waiting room)
will be shown. At the waiting room you can:
- See the list of other online players, and refresh the list by pressing update button
- Select a user from that list and either chat or play with her

Note that you will be able to chat with your opponent when you're playing the game.

## Notes
- You need to connect to the same Wi-Fi with your opponent
- The default port is 12345 for UDP and TCP packets(except for the message packets during the game)
- The game chat port is 1234 for TCP packets(just for the message packets during the game)
- Selected development platform is MacOS using Python 3.8.5
- Required packages can be found in requirements.txt file detaily

## Partner
- We have implemented this project together with my friend [Ahmet Senturk](https://github.com/ahmetsenturk/).

## License
- [BSD 3](https://github.com/ahmetsenturk/CMPE487-ConnectFourGame/blob/sertay/LICENSE)

## Extras
- [PySimpleGui some infos](https://pysimplegui.readthedocs.io/en/latest/cookbook/)
