# comms.py
import serial
from config import SERIAL_PORT, BAUD_RATE

class SerialManager:
    def __init__(self):
        self.ser = None
        self.buffer = ""
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
            self.ser.reset_input_buffer()
            print(f"[COMMS] Connected to {SERIAL_PORT}")
        except Exception as e:
            print(f"[COMMS] Warning: Connection failed ({e}). Simulating...")

    def send(self, command):
        """ Send a string command to PIC """
        if self.ser:
            try:
                self.ser.write(command.encode())
            except Exception as e:
                print(f"[COMMS] Send Error: {e}")

    def read_commands(self):
        """ Returns a list of complete commands received from PIC """
        commands = []
        if self.ser and self.ser.in_waiting > 0:
            try:
                # Read data and append to internal buffer
                data = self.ser.read(self.ser.in_waiting).decode('utf-8', errors='ignore')
                self.buffer += data
                
                # Extract complete lines (commands)
                while '\n' in self.buffer:
                    line, self.buffer = self.buffer.split('\n', 1)
                    line = line.strip()
                    if line:
                        commands.append(line)
            except Exception:
                pass
        return commands

    def close(self):
        if self.ser:
            self.send('X') # Turn off any outputs
            self.ser.close()