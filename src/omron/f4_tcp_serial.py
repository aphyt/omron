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

    def send_command_long_response(self, command: bytes) -> bytes:
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

    def send_command(self, command: bytes) -> bytes:
        attempts = 0
        self.socket.sendall(command)
        data_buffer = b''
        while True:
            try:
                data = self.socket.recv(1024)
                data_buffer += data
                attempts = 0
                if data[-1] == 3:
                    # The ETX is UTF-8 3 and indicates the message has completed
                    break
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
        response = self.send_command_long_response(command)
        with open(file_name, "wb") as binary_file:
            binary_file.write(response)

    def trigger_inspection(self):
        command = bytes('TRIGGER\r', 'utf-8')
        response = self.send_command_long_response(command)
        return response

    def get(self, area: str):
        command_string = 'GET'
        command_string += f' {area}'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        response = response.decode('utf-8').rstrip('\3')
        response = response.rstrip()
        return response

    def set(self, area: str, data: str):
        command_string = 'SET'
        command_string += f' {area} {data}'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        response = response.decode('utf-8').rstrip('\3')
        response = response.rstrip()
        return response

    def help(self):
        command_string = 'HELP'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        response = response.decode('utf-8').rstrip('\3')
        response = response.rstrip()
        return response

    def info(self, data: str = None):
        command_string = 'INFO'
        if data:
            command_string += f' {data}'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        response = response.decode('utf-8').rstrip('\3')
        response = response.split('\r\n')
        return response

    def print_info_tree(self, start='', indent=''):
        current_value = start
        values = self.info(start)
        for value in values:
            if value != '':
                output = indent + value
                print(output)
                next_indent = '  ' + indent
                if current_value != '':
                    value = current_value + '.' + value
                self.print_info_tree(value, next_indent)

    def get_string(self, number: int):
        """Get the string stored in the camera at the specified attribute number"""
        assert number >= 1
        assert number <= 200
        response = self.get(f'string{number}')
        return response

    def set_string(self, number: int, value: str):
        """Set the string stored in the camera at the specified attribute number"""
        assert number >= 1
        assert number <= 200
        response = self.set(f'string{number}', value)
        return response

    def get_bool(self, number: int):
        """Get the Boolean stored in the camera at the specified attribute number"""
        assert number >= 1
        assert number <= 200
        response = False
        if self.get(f'bool{number}') == '1':
            response = True
        return response

    def set_bool(self, number: int, value: bool):
        """Set the Boolean stored in the camera at the specified attribute number"""
        assert number >= 1
        assert number <= 200
        if value:
            self.set(f'bool{number}', '1')
        else:
            self.set(f'bool{number}', '0')

    def get_int(self, number: int):
        """Get the 16-bit Integer stored in the camera at the specified attribute number"""
        assert number >= 1
        assert number <= 200
        response = self.get(f'int{number}')
        response = int(response)
        return response

    def set_int(self, number: int, value: int):
        """Set the 16-bit Integer stored in the camera at the specified attribute number"""
        assert number >= 1
        assert number <= 200
        value = str(value)
        response = self.set(f'int{number}', value)
        return response

    def get_long(self, number: int):
        """Get the 32-bit Integer stored in the camera at the specified attribute number"""
        assert number >= 1
        assert number <= 200
        response = self.get(f'long{number}')
        response = int(response)
        return response

    def set_long(self, number: int, value: int):
        """Set the 32-bit Integer stored in the camera at the specified attribute number"""
        assert number >= 1
        assert number <= 200
        value = str(value)
        response = self.set(f'long{number}', value)
        return response

    def get_float(self, number: float):
        """Get the Floating Point stored in the camera at the specified attribute number"""
        assert number >= 1
        assert number <= 200
        response = self.get(f'float{number}')
        response = float(response)
        return response

    def set_float(self, number: int, value: float):
        """Set the Floating Point stored in the camera at the specified attribute number"""
        assert number >= 1
        assert number <= 200
        value = str(value)
        response = self.set(f'float{number}', value)
        return response

    def job_info(self, data: str = None):
        command_string = 'JOBINFO'
        if data:
            command_string += f' {data}'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        response = response.decode('utf-8').rstrip('\3')
        response = response.rstrip()
        return response
