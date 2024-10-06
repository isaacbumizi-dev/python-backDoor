# python-backDoor
This Python project creates a backdoor that allows for complete remote control of a computer. Features include:  Control of the camera and microphone Remote command execution Real-time monitoring Note: This project is intended for educational purposes only. Using this code to access systems without authorization is illegal.

How to use it?

First, start the server with the command: python server -lhos="server IP address" -p="server port". Once the client is connected, you can send commands.

Commands to send:

1. --help :> show this message
2. screenshoot :> take a screenshot
3. upload + "file name" :> upload a file
4. download -f + "file name" :> download a file
5. download -d + "folder name" :> download a folder
6. execute + "file name" :> run an executable file
7. show connection :> show all connections on the server
8. set-connection + "socket number" :> redirect a connection to the corresponding socket number
9. record + "recording time (in seconds)" :> record audio on the victim’s machine
10. camShoot :> take a picture with the victim’s machine camera
11. disk_partitions or disk partitions :> show current disk partitions on the target machine
