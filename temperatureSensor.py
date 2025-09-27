# Micropython class for temperature sensor
import AD7415.AD7415 as AD7415
from machine import Pin, I2C
import time

class temperatureSensor:
    def __init__(self):
        # Initialize sensor hardware
        self.i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=100000)
        self.tsensor = AD7415.AD7415(self.i2c)
 
    def readTemperature(self):
        return(self.tsensor.read_Temperature())

if __name__ == "__main__":
    # Hello Temperature Sensor!
    temp_sensor = temperatureSensor()
    for i in range(10):
        print(temp_sensor.readTemperature())
