"""
MicroPython Class for AD7415 ±0.5°C Accurate, 10-Bit Digital Temperature Sensor in SOT-23
Sep 25, 2025, Papamidas (DM1CR)

"""
import machine

class AD7415:

    def __init__(self, i2c, adr=73):
        """
        Create AD7415 instance

        Args:
            i2c: configured SPI bus
            adr: I2C address of AD7415
                 AD7415-0: AS=float, adr=0x48=72
                           AS=GND, adr=0x49=73
                           AS=Vdd, adr=0x4a=74
                 AD7415-1: AS=float, adr=0x4c=76
                           AS=GND, adr=0x4d=77
                           AS=Vdd, adr=0x4e=78
        """
        self._i2c = i2c
        self._adr = adr

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        pass
    
    def bytearray_to_celsius(self, _inb):
        adcval = ((((_inb[0] << 8) & 0x7f00) + _inb[1]) >> 6)
        if (_inb[0] & 0x80):
            #negative celsius temperature
            adcval -= 512
        return(adcval/4)
            
    def read_Temperature(self) -> float:
        outb = bytearray(1)
        outb[0] = 0x00
        self._i2c.writeto(self._adr, outb)
        inb = bytearray(2)
        self._i2c.readfrom_into(self._adr, inb)
        return(self.bytearray_to_celsius(inb))
    
if __name__ == "__main__":
    # Hello World!
    from machine import Pin, I2C
    import time
    i2c = machine.I2C(0, scl=Pin(9), sda=Pin(8), freq=100000)
    with AD7415(i2c) as ad7415:
        print("I²C address: ", ad7415._adr)
        
        #test register values to temperature conversion with
        #some test vectors from the data sheet:
        inb=bytearray(2)
        inb[0] = 0b11001001
        inb[1] = 0b00000000
        print( "-55°C", inb[0], inb[1], ad7415.bytearray_to_celsius(inb) )
        inb[0] = 0b11001110
        inb[1] = 0b00000000
        print( "-50°C", inb[0], inb[1], ad7415.bytearray_to_celsius(inb) )
        inb[0] = 0b11100111
        inb[1] = 0b00000000
        print( "-25°C", inb[0], inb[1], ad7415.bytearray_to_celsius(inb) )
        inb[0] = 0b11111111
        inb[1] = 0b11000000
        print( "-0.25°C", inb[0], inb[1], ad7415.bytearray_to_celsius(inb) )
        inb[0] = 0b00000000
        inb[1] = 0b00000000
        print( "0°C", inb[0], inb[1], ad7415.bytearray_to_celsius(inb) )
        inb[0] = 0b00000000
        inb[1] = 0b01000000
        print( "0.25°C", inb[0], inb[1], ad7415.bytearray_to_celsius(inb) )
        inb[0] = 0b00001010
        inb[1] = 0b00000000
        print( "10°C", inb[0], inb[1], ad7415.bytearray_to_celsius(inb) )
        inb[0] = 0b00011001
        inb[1] = 0b00000000
        print( "25°C", inb[0], inb[1], ad7415.bytearray_to_celsius(inb) )
        inb[0] = 0b00110010
        inb[1] = 0b00000000
        print( "50°C", inb[0], inb[1], ad7415.bytearray_to_celsius(inb) )
        inb[0] = 0b01001011
        inb[1] = 0b00000000
        print( "75°C", inb[0], inb[1], ad7415.bytearray_to_celsius(inb) )
        inb[0] = 0b01100100
        inb[1] = 0b00000000
        print( "100°C", inb[0], inb[1], ad7415.bytearray_to_celsius(inb) )
        inb[0] = 0b01111101
        inb[1] = 0b00000000
        print( "125°C", inb[0], inb[1], ad7415.bytearray_to_celsius(inb) )
        
        #now read in the current temperature from the actual device:
        for cnt in range(100):
            print("Temperature: ", ad7415.read_Temperature())
            time.sleep(1)
        