# MicroPython rfDiodeSensor class
import voltageSensor
import temperatureSensor

class rfDiodeSensor:
    def __init__(self, voltageSensor, temperatureSensor):
        self.voltageSensor = voltageSensor
        self.temperatureSensor = temperatureSensor

    def readVoltage(self):
        return self.voltageSensor.readVoltage()

    def readTemperature(self):
        return self.temperatureSensor.readTemperature()

    def readPower(self):
        # Example: simple linear conversion, replace with real formula as needed
        voltage = self.readVoltage()
        temperature = self.readTemperature()
        # For demonstration, assume power = voltage * (1 + 0.01*(temperature-25))
        return voltage * (1 + 0.01 * (temperature - 25))

if __name__ == "__main__":
    vsensor=voltageSensor.voltageSensor()
    tsensor=temperatureSensor.temperatureSensor()
    rfds = rfDiodeSensor(vsensor, tsensor)
    
    print("Voltage: ", rfds.readVoltage())
    print("Temperature: ", rfds.readTemperature())
    print("Power: ", rfds.readPower())
