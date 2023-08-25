__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import asyncio
import socket
import errno
import time
import select


class ImageRectangle:
    def __init__(self, upper_left_x: int, upper_left_y: int, lower_right_x: int, lower_right_y: int):
        self.upper_left_x = upper_left_x
        self.upper_left_y = upper_left_y
        self.lower_right_x = lower_right_x
        self.lower_right_y = lower_right_y


class F4TCPSerial:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host: str, port: int = 49211):
        self.socket.connect((host, port))
        self.socket.setblocking(False)

    def close(self):
        self.socket.close()

    def send_command(self, command: bytes) -> bytes:
        attempts = 0
        self.socket.sendall(command)
        data_buffer = b''
        while True:
            try:
                data = self.socket.recv(1024)
                data_buffer += data
                attempts = 0
                if not data:
                    self.socket.close()
                    break
                else:
                    pass
            except socket.error as e:
                if e.args[0] == errno.EWOULDBLOCK:
                    if attempts < 100:
                        attempts += 1
                        time.sleep(0.01)
                    else:
                        break
                else:
                    print(e)
                    break
        return data_buffer

    def get_image(self, file_name: str,
                  image_format: str = None,
                  quality: int = None,
                  image_area: ImageRectangle = None,
                  inspection_number: int = None):
        command_string = 'GETIMAGE'
        if image_format is not None:
            command_string += f' -format={image_format}'
        if quality is not None:
            command_string += f' -quality={str(quality)}'
        if inspection_number is not None:
            command_string += f' -inspection={str(inspection_number)}'
        command = bytes(command_string+'\r', 'utf-8')
        response = self.send_command(command)
        with open(file_name, "wb") as binary_file:
            binary_file.write(response)

    def trigger_inspection(self):
        command = bytes('TRIGGER\r', 'utf-8')
        response = self.send_command(command)
        return response

    def get(self, area: str):
        command_string = 'GET'
        command_string += f' {area}'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        return response

    def set(self, area: str, data: str):
        command_string = 'SET'
        command_string += f' {area} {data}'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        return response
