'''
Created on 11.08.2026

@author: Ruber
'''
import serial


class RadarCLI:

    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=1
        )

    def send_command(self, command):
        command = command.strip()

        if not command:
            return

        print(f">>> {command}")

        self.ser.write((command + "\r\n").encode("ascii"))
        self.ser.flush()

        response = self.ser.read_until(b"Done\r\n")

        if response:
            print(
                response.decode(
                    "ascii",
                    errors="replace"
                ),
                end=""
            )

    def send_config(self, config):
        for line in config.splitlines():

            line = line.strip()

            if not line:
                continue

            if line.startswith("%"):
                continue

            self.send_command(line)

    def close(self):
        self.ser.close()