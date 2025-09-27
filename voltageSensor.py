# Micropython class for voltage sensor

import AD7791.AD7791 as AD7791
from machine import Pin, SPI
import time

class voltageSensor:
    def __init__(self):
        # Initialize ADC hardware
        self.nRDY = Pin(4)
        self.spi = SPI(0, baudrate=100000, polarity=1, phase=1, bits=8,\
                       firstbit=SPI.MSB, sck=Pin(6), mosi=Pin(7), miso=self.nRDY)
        self.adc = AD7791.AD7791(self.spi, self.nRDY, ref_voltage=2.5)
        self.adc.reset()
        #set filter to CDIV1, 16.6sps:
        self.adc.write_filter("CDIV1", "16.6sps")

    def readVoltage(self):
        #start unipolar single conversion
        _maxtries = 2000
        _ctr=0
        self.adc.start_unipolar_single_conversion()
        for _i in range(_maxtries):
            time.sleep_ms(1);
            _ctr+=1
            if(self.adc.nRDY.value() == 0):
                break
        if _ctr < _maxtries:
            _v = self.adc.read_unipolar_ADC_voltage()
        else:
            _v = 0.0
        return(_v)

if __name__ == "__main__":
    # Hello Voltage Sensor!
    volt_sensor = voltageSensor()
    for i in range(10):
        print(volt_sensor.readVoltage())