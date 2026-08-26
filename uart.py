import serial


class UARTReader:
    def __init__(self,
                 port: str,
                 baudrate: int = 921600,
                 timeout: float = 0.1):

        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout
        )

    def read(self, size: int = 1024) -> bytes:
        return self.ser.read(size)

    def bytes_waiting(self) -> int:
        return self.ser.in_waiting

    def close(self):
        if self.ser.is_open:
            self.ser.close()