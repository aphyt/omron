# Omron F430 and F440 Vision Sensor

```python
import f4_tcp_serial


if __name__ == '__main__':
    f4_instance = f4_tcp_serial.F4TCPSerial()
    f4_instance.connect("192.168.250.15")
    f4_instance.get_image('file.jpg')
    f4_instance.close()
```