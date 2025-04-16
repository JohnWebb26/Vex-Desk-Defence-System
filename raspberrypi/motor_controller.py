import serial

class MotorController:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate, timeout=1)

    def move(self, x, y):
        x_angle = int((x / 640) * 180)
        y_angle = int((y / 480) * 180)
        self.ser.write(f"X{x_angle}Y{y_angle}\n".encode())

    def __del__(self):
        if self.ser.is_open:
            self.ser.close()
