# Documentation
## Installation and Upgrade
### Installation from PyPi

`pip install omron`

### Upgrade from PyPi

`pip install omron --upgrade`

## Usage

### Send String to Match Code Read Inspection

Using an AutoVision job where the sensor project has:

- Linked the Status of Code Read Inspection to Boolean 1
- Linked the Inspection's Match String to String Input 101 

The following code will send a string to match in the QR code read, trigger the inspection, and then retrieve the Boolean value that indicates whether the inspection matched. 

```python
from omron import f4_tcp_serial


if __name__ == '__main__':
    f4_instance = f4_tcp_serial.F4TCPSerial()
    f4_instance.connect('192.168.250.15')
    f4_instance.go_online()

    f4_instance.set_string(101, 'https://omron.com')
    f4_instance.trigger_inspection()
    print(f'The result of the inspection match is: {f4_instance.get_bool(1)}')

    f4_instance.set_string(101, 'https://aphyt.com')
    f4_instance.trigger_inspection()
    print(f'The result of the inspection match is: {f4_instance.get_bool(1)}')

    f4_instance.close()
```

This inspection fails when the QR code text does not match what was sent to String 101 and succeeds when String 101 is changed to the correct value and the inspection rerun as demonstrated by the results of the code execution below. 

#### Response
```
The result of the inspection match is: False
The result of the inspection match is: True
```


### Get Inspection Image

This code will connect to an F4 camera located at IP Address 192.168.250.15 and transfer the last inspection image to the client PC to be stored as 'file.jpg'.

```python
from omron import f4_tcp_serial


if __name__ == '__main__':
    f4_instance = f4_tcp_serial.F4TCPSerial()
    f4_instance.connect('192.168.250.15')
    f4_instance.get_image('file.jpg')
    f4_instance.close()
```

### Transfer AVP Job to Client PC from Camera Slot

This code with connect to an F4 camera and then transfer the AVP in slot 5 to the client PC. The job stored in slot 5 is "Code Read Job.avp", so after execution of this program a local file will be created with this same name and file contents. 

```python
from omron import f4_tcp_serial


if __name__ == '__main__':
    f4_instance = f4_tcp_serial.F4TCPSerial()
    f4_instance.connect('192.168.250.15')
    f4_instance.transfer_job_from_camera(5)
```

### Transfer Running Job to Client PC

This code with connect to an F4 camera and then transfer the currently executing AVP job to the client PC. The AVP file will be named as a concatenation of the current date and time string, with the name of the camera to avoid name collisions that might overwrite other files. 

```python
from omron import f4_tcp_serial


if __name__ == '__main__':
    f4_instance = f4_tcp_serial.F4TCPSerial()
    f4_instance.connect('192.168.250.15')
    f4_instance.transfer_running_job_from_camera()
```

### Transfer AVP from Client PC to Camera Slot

This code with connect to an F4 camera and then transfer the AVP file "Code Read Job.av" from the client PC to the camera and put it in job slot 2. 

```python
from omron import f4_tcp_serial


if __name__ == '__main__':
    f4_instance = f4_tcp_serial.F4TCPSerial()
    f4_instance.connect('192.168.250.15')
    f4_instance.transfer_job_to_camera('Code Read Job.avp', 2)
```
