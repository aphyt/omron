# Documentation
## Installation and Upgrade
### Installation from PyPi

`pip install omron`

### Upgrade from PyPi

`pip install omron --upgrade`

## Usage

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