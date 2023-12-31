__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

import asyncio
import ftplib
import os.path
import socket
import errno
import time
import select
from ftplib import FTP
from typing import List
from datetime import datetime


class ImageRectangle:
    def __init__(self, upper_left_x: int, upper_left_y: int, lower_right_x: int, lower_right_y: int):
        self.upper_left_x = upper_left_x
        self.upper_left_y = upper_left_y
        self.lower_right_x = lower_right_x
        self.lower_right_y = lower_right_y


class F4TCPSerial:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.camera_name = None
        self.connected_host = None
        self.ftp_job_location = '/sd0:0/Jobs/Job1'

    def connect(self, host: str, port: int = 49211):
        self.socket.connect((host, port))
        self.connected_host = host
        self.socket.setblocking(False)

    def close(self):
        self.connected_host = None
        self.socket.close()

    def get_camera_name(self):
        self.camera_name = self.get('system.name')
        return self.camera_name

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

    def go_offline(self):
        command_string = f'OFFLINE'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        response = response.decode('utf-8').rstrip('\3')
        response = response.rstrip()
        return response

    def go_online(self):
        command_string = f'ONLINE'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        response = response.decode('utf-8').rstrip('\3')
        response = response.rstrip()
        return response

    def get_online_status(self):
        command_string = f'ONLINE?'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        response = response.decode('utf-8').rstrip('\3')
        response = response.rstrip()
        return response

    def job_save(self, slot_number: int = None):
        command_string = f'JOBSAVE -slot={str(slot_number)}'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        response = response.decode('utf-8').rstrip('\3')
        response = response.rstrip()
        return response

    def job_save_as(self, job_name: str, slot_number: int = None):
        command_string = f'JOBSAVEAS -slot={str(slot_number)} -name={job_name}'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        response = response.decode('utf-8').rstrip('\3')
        response = response.rstrip()
        return response

    def job_load(self, slot_number: int = None):
        command_string = f'JOBLOAD -slot={str(slot_number)} -r'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        response = response.decode('utf-8').rstrip('\3')
        response = response.rstrip()
        self.go_online()
        while self.get_online_status() != '!1':
            time.sleep(.1)
        return response

    def job_delete_slot(self, slot_number: int):
        """Delete job in the specified slot"""
        command_string = f'JOBDELETE -slot={slot_number}'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        response = response.decode('utf-8').rstrip('\3')
        response = response.rstrip()
        return response

    def job_delete_all(self):
        """Delete all job slots"""
        command_string = f'JOBDELETE -all'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        response = response.decode('utf-8').rstrip('\3')
        response = response.rstrip()
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

    def job_download(self, size_in_bytes: int = None):
        command_string = 'JOBDOWNLOAD -transfer=ftp'
        if size_in_bytes:
            command_string += f' -size={size_in_bytes}'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        response = response.decode('utf-8').rstrip('\3')
        response = response.rstrip()
        return response

    def job_download_cancel(self):
        command_string = 'JOBDOWNLOAD -c'
        command = bytes(command_string + '\r', 'utf-8')
        response = self.send_command(command)
        response = response.decode('utf-8').rstrip('\3')
        response = response.rstrip()
        return response

    def get_used_job_slots(self) -> List[int]:
        """Get the used job slot numbers"""
        job_info_response = self.job_info()
        jobs = job_info_response.rsplit('\r\n')
        slots = []
        for job in jobs:
            slot = int(job.rsplit('=')[0][4:])
            slots.append(slot)
        return slots

    def get_next_available_job_slot(self):
        """Get the next available job slot"""
        used_slots = self.get_used_job_slots()
        next_slot = None
        if used_slots[0] != 1:
            next_slot = 1
        else:
            for index, slot in enumerate(used_slots):
                if index + 1 == slot:
                    pass
                else:
                    next_slot = index + 1
        return next_slot

    def transfer_running_job_from_camera(self,
                                         username: str = 'target',
                                         password: str = 'password',
                                         path: str = None):
        available_slot = self.get_next_available_job_slot()
        current_time = datetime.now()
        current_time = current_time.strftime('%Y-%m-%dT%H-%M-%S')
        common_name = f'{current_time}_{self.get_camera_name()}'
        self.job_save_as(common_name, available_slot)
        self.transfer_job_from_camera(available_slot, username, password, path)
        self.job_delete_slot(available_slot)

    def transfer_job_from_camera(self, slot_number: int,
                                 username: str = 'target',
                                 password: str = 'password',
                                 path: str = None):
        available_slot = self.get_next_available_job_slot()
        avp_name = self.job_info(str(slot_number)).rsplit('=')[1]
        ftp_save_name = f'slot{slot_number}_{avp_name}'
        # Create an FTP to retrieve AVP
        ftp_client = FTP(self.connected_host, username, password)
        # Change to the directory where the saved AVP is stored
        ftp_client.cwd(self.ftp_job_location)
        # Retrieve file to the local machine
        if path is None:
            avp_name = os.path.join(os.getcwd(), avp_name)
        else:
            avp_name = os.path.join(path, avp_name)
        with open(avp_name, 'wb') as fp:
            ftp_client.retrbinary(f'RETR {ftp_save_name}', fp.write)
        self.job_delete_slot(available_slot)

    def transfer_job_to_camera(self, job_avp: str, slot_number: int,
                               username: str = 'target', password: str = 'password'):
        ftp_save_name = f'slot{slot_number}_{job_avp}'
        ftp_client = FTP(self.connected_host, username, password)
        # Change to the directory where the saved AVP is stored
        ftp_client.cwd(self.ftp_job_location)
        # Retrieve file to the local machine
        with open(job_avp, 'rb') as fp:
            ftp_client.storbinary(f'STOR {ftp_save_name}', fp)


