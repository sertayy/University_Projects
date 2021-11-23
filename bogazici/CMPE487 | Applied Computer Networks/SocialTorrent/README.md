# Social Torrent

Program that creates a chat server using python socket library. Users can can send a message or a file to another user on the network. 
Users also can send and receive file from the other users on the network via torrent. 

## running

To run the program enter this into the terminal:


```sh
$ python3 chat.py
```

Program automatically will send a UDP broadcast message to other users on the same network. After that, user is free to chat with the people on the network.

Later program asks the user whether she wants to chat, send file or use torrent system. 

- To chat, simply enter "chat" then your message and to whom you want to send this message. 

- To send file, enter "file" then which file you want to send and to who.

- To use the torrent system enter command "torrent". The program will then ask you whether you want to download from or upload to the torrent system.
  - If user selects download the program will sends a torrent discovery message to all users on the network to gather the files on the torrent system.
Then will ask the user to choose a file from these gathered torrent files. 
  - If user selects upload, program will ask user to choose a file to upload to torrent system. This selected file should be in my_files folder, which also 
should be on the same directory with chat.py file. After that, the chunks of the selected file will be distributed to the clients.

Contributers: 

- Ahmet Ibrahim Senturk
- Ahmet Yigit Gedik
- Sertay Akpinar

Remarks:
- We've implemented the bonus part.
- This program is written on MacOS environment using python 3.7.
- All the packages used in this projects are built-in packages. That's why requirements.txt is empty. 
- You can access your chat history in the "chat_history.txt" file created inside the project folder after executing the program.
- The program assumes that all the users have different usernames, hence, same usernames might lead to confusion. 
