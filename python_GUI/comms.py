import serial
import time

class SerialManager:
    """
    Handles Serial (UART) communication between the Python Game and the PIC Microcontroller.
    """

    def __init__(self, port, baudrate=9600):
        """
        Initialize the serial connection.
        :param port: The COM port (e.g., 'COM3')
        :param baudrate: Communication speed (default 9600)
        """
        try:
            # Initialize Serial Object with a short timeout for non-blocking reads
            self.serial = serial.Serial(port, baudrate, timeout=0.1)
            
            # Wait a moment for the connection to stabilize
            time.sleep(2) 
            print(f"[SERIAL] Connected to {port}")
        except serial.SerialException as e:
            print(f"[SERIAL] Error connecting to {port}: {e}")
            self.serial = None

    def read_commands(self):
        """
        Reads all available data from the serial buffer.
        Returns a list of clean command strings (e.g., ['POT:500', 'BTN:1']).
        """
        commands = []
        # Check if serial is open and there is data waiting
        if self.serial and self.serial.in_waiting > 0:
            try:
                # Read all bytes and decode to UTF-8
                raw_data = self.serial.read(self.serial.in_waiting).decode('utf-8', errors='ignore')
                
                # Split the raw data by newline characters to get individual commands
                lines = raw_data.split('\n')
                for line in lines:
                    line = line.strip() # Remove whitespace
                    if line:
                        commands.append(line)
            except Exception as e:
                print(f"[SERIAL] Read Error: {e}")
        return commands

    def send(self, message):
        """
        Sends a string message to the PIC Microcontroller.
        """
        if self.serial:
            try:
                self.serial.write(message.encode('utf-8'))
            except Exception as e:
                print(f"[SERIAL] Send Error: {e}")

    def close(self):
        """
        Closes the serial connection safely.
        """
        if self.serial:
            self.serial.close()