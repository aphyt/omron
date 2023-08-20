__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import asyncio
import socket
import errno
import time
import select


class F4TCPSerial:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_buffer = b''

    def connect(self, host: str, port: int = 49211):
        self.socket.connect((host, port))
        self.socket.setblocking(False)

    def close(self):
        self.socket.close()

    def get_image(self, file_name: str):
        command = bytes('GETIMAGE\r', 'utf-8')
        self.socket.sendall(command)
        while True:
            try:
                data = self.socket.recv(1024)
                self.data_buffer += data
                if not data:
                    self.socket.close()
                    break
                else:
                    pass
            except socket.error as e:
                if e.args[0] == errno.EWOULDBLOCK:
                    if len(self.data_buffer) == 0:
                        time.sleep(1)
                    else:
                        break
                else:
                    print(e)
                    break

        with open(file_name, "wb") as binary_file:
            binary_file.write(self.data_buffer)


