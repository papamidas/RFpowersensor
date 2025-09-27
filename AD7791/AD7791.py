"""
MicroPython Class for AD7791 Low Power, Buffered 24-Bit Sigma-Delta ADC
Sep 7, 2025, Papamidas (DM1CR)

"""
import machine

# Status register bits

__AD7791_STATUS_REG = 0x00     #RS1 = 0 RS0 = 0: Status register (read only)
__AD7791_MODE_REG   = 0x10     #RS1 = 0 RS0 = 1: Mode register (read/write)
__AD7791_FILTER_REG = 0x20     #RS1 = 1 RS0 = 0: Filter register (read/write)
__AD7791_DATA_REG   = 0x30     #RS1 = 1 RS0 = 1: Data register (read only)

__AD7791_READ_OP    = 0x08     #R = 1: next operation is read specified register
__AD7791_WRITE_OP   = 0x00     #R = 0: next operation is write specified register

__AD7791_CONTINUOUS_READ = 0x04 #CREAD = 1: Continuous read of Data register

__AD7791_CHANSEL_AIN   = 0x00   #CH1 = 0 CH0 = 0: AIN(+)-AIN(-)
__AD7791_CHANSEL_SHORT = 0x02   #CH1 = 1 CH0 = 0: AIN(-)-AIN(-)
__AD7791_CHANSEL_VDD   = 0x03   #CH1 = 1 CH0 = 1: Vdd Monitor (Vdd/5, Vref=1.17V onchip)

# Mode register bits

__AD7791_CONTINUOUS_CONVERSION_MODE = 0x00 #MD1 = 0 MD0 = 0: Continuous conversion mode
__AD7791_SINGLE_CONVERSION_MODE     = 0x80 #MD1 = 1 MD0 = 0: Single conversion mode
__AD7791_POWER_DOWN_MODE            = 0xc0 #MD1 = 1 MD0 = 1: Power down mode

__AD7791_BURNOUT_CURRENT_DISABLE = 0x00 #BO = 0
__AD7791_BURNOUT_CURRENT_ENABLE  = 0x08 #BO = 1
__AD7791_UNIPOLAR_CODING = 0x04 #U/B = 1: set unipolar coding 0x000000..0xffffff
__AD7791_BIPOLAR_CODING  = 0x00 #U/B = 0: set bipolar coding 0x000000..0x80000..0xffffff
__AD7791_BUFFER_ENABLE = 0x02   #BUF = 1
__AD7791_BUFFER_DISABLE = 0x00  #BUF = 0

# Filter register bits

__AD7791_NORMAL_MODE  = 0x00 #CLKDIV1 = 0 CLKDIV0 = 0: Normal Mode
__AD7791_CLKDIV2_MODE = 0x10 #CLKDIV1 = 0 CLKDIV0 = 1: Clock Divided by 2
__AD7791_CLKDIV4_MODE = 0x20 #CLKDIV1 = 1 CLKDIV0 = 0: Clock Divided by 4
__AD7791_CLKDIV8_MODE = 0x30 #CLKDIV1 = 1 CLKDIV0 = 1: Clock Divided by 8

__AD7791_UPDATE_RATE_DEFAULT = 0x04 #65dB@50Hz/60Hz rejection
__AD7791_FS2 = 0x04
__AD7791_FS1 = 0x02
__AD7791_FS0 = 0x01

# Conversion modes

__AD7791_CONTINUOUS = 0
__AD7791_SINGLE = 2
__AD7791_POWERDOWN = 3

class AD7791:

    def __init__(self, spi, nRDY, ref_voltage=2.5):
        """
        Create AD7791 instance

        Args:
            spi: configured SPI bus
            ref_voltage: Vref value
        """
        self._spi = spi
        self._nRDY = nRDY
        self._ref_voltage = ref_voltage
        self._conversion_mode = __AD7791_CONTINUOUS

    @property
    def ref_voltage(self) -> float:
        """Returns reference voltage as float"""
        return self._ref_voltage

    @ref_voltage.setter
    def ref_voltage(self, newrefvoltage):
        if(newrefvoltage >= 0.1 and newrefvoltage <= 5.0):
            self._ref_voltage = newrefvoltage
        else:
            print("ref voltage out range, must be 0.1V..Vdd")

    @property
    def nRDY(self):
        """Returns nRDY/DOUT/MISO pin object"""
        return self._nRDY

    def reset(self):
        """Resets ADC to its default state"""
        outbuf = bytearray(4)
        outbuf[0] = 0xff
        outbuf[1] = 0xff
        outbuf[2] = 0xff
        outbuf[3] = 0xff
        self._spi.write(outbuf)

    def read_status(self):
        """Reads Status Register"""
        outb = bytearray(1)
        outb[0] = __AD7791_STATUS_REG + __AD7791_READ_OP
        #print("outb = ", outb)
        self._spi.write(outb)
        inb = bytearray(1)
        self._spi.readinto(inb)
        #print("inb[0] hex = ", hex(inb[0]))
        return inb
        
    def print_status(self, status):
        """Prints the meaning of status register bits"""
        print("status register (hex): ", hex(status))
        if (status & 0x80):
            print("not ready (1)")
        else:
            print("ready (0)")
        if (status & 0x40):
            print("ADC ERR")
        else:
            print("ADC OK")
        if (status & 0x04):
            print("ADC is AD7791")
        else:
            print("ADC is AD7790")
        ch = status & 0x03
        if ch == 0:
            print("channel selection AIN(+)-AIN(-)")
        elif ch == 1:
            print("Reserved")
        elif ch == 2:
            print("channel selection SHORT AIN(-)-AIN(-)")
        elif ch == 3:
            print("channel selection Vdd Monitor")
                
    def read_mode(self):
        """Reads Mode Register"""
        outb = bytearray(1)
        outb[0] = __AD7791_MODE_REG + __AD7791_READ_OP
        self._spi.write(outb)
        inb = bytearray(1)
        self._spi.readinto(inb)
        return inb
    
    
    def print_mode(self, mode):
        """Prints the meaning of modes register bits"""
        print("mode register (hex): ", hex(mode))
        op = mode & 0xc0
        if op == 0x00:
            print("continuous conversion mode")
        elif op == 0x40:
            print("reserved mode")
        elif op == 0x80:
            print("single conversion mode")
        elif op == 0xc0:
            print("power down mode")
        if mode & 0x30 != 0:
            print("!!!MR4, MR5 must be 0")
        if mode & 0x08 != 0:
            print("Burnout Current enabled!")
        if mode & 0x04 == 0x04:
            print("Unipolar Coding selected")
        else:
            print("Bipolar Coding selected")
        if mode & 0x02 == 0x02:
            print("Buffer enabled")
        else:
            print("Buffer disabled")
        if mode & 0x01 == 0x01:
            print("!!!MR0 must be 0")

    def read_filter(self):
        """Reads Filter Register"""
        outb = bytearray(1)
        outb[0] = __AD7791_FILTER_REG + __AD7791_READ_OP
        self._spi.write(outb)
        inb = bytearray(1)
        self._spi.readinto(inb)
        return inb

    def write_filter(self, cdiv, fadc):
        """Writes Filter Register"""
        _cdiv = {
            "CDIV1": __AD7791_NORMAL_MODE,
            "CDIV2": __AD7791_CLKDIV2_MODE,
            "CDIV4": __AD7791_CLKDIV4_MODE,
            "CDIV8": __AD7791_CLKDIV8_MODE
        }
        _fadc = {
            "120sps" :  0,
            "100sps" :  __AD7791_FS0,
            "33.3sps":  __AD7791_FS1,
            "20sps"  :  __AD7791_FS1 + __AD7791_FS0,
            "16.6sps":  __AD7791_UPDATE_RATE_DEFAULT,
            "16.7sps":  __AD7791_FS2 + __AD7791_FS0,
            "13.3sps":  __AD7791_FS2 + __AD7791_FS1,
            "9.5sps" :  __AD7791_FS2 + __AD7791_FS1 + __AD7791_FS0
        }
        outb = bytearray(2)
        outb[0] = __AD7791_FILTER_REG + __AD7791_WRITE_OP
        outb[1] = _cdiv[cdiv] + _fadc[fadc]
        self._spi.write(outb)

    def print_filter(self, filter):
        """Prints the meaning of filter register bits"""
        print("filter register (hex): ", hex(filter))
        if filter & 0xc0 != 0:
            print("!!!FR7, FR6 must be 0")
        cdiv = filter & 0x30
        if cdiv == 0x00:
            print("normal mode")
        elif cdiv == 0x10:
            print("Clock divided by 2")
        elif cdiv == 0x20:
            print("Clock divided by 4")
        elif cdiv == 0x30:
            print("Clock divided by 8")
        if filter & 0x08 != 0:
            print("!!!FR3 must be 0")
        updates = filter & 0x07
        print("update rate ", str(updates), " selected")
        
    def start_unipolar_single_conversion(self):
        """writes Mode Register for single normal AIN(+)-AIN(-) conversion"""
        outb = bytearray(2)
        outb[0] = __AD7791_MODE_REG + __AD7791_WRITE_OP + __AD7791_CHANSEL_AIN
        outb[1] = __AD7791_SINGLE_CONVERSION_MODE + \
                  __AD7791_BURNOUT_CURRENT_DISABLE + \
                  __AD7791_UNIPOLAR_CODING + \
                  __AD7791_BUFFER_ENABLE
        self._spi.write(outb)
        self._conversion_mode = __AD7791_SINGLE

    def set_coding(self, coding):
        """writes Mode Register for unipolar/bipolar conversion"""
        """mode should be either
           __AD7791_UNIPOLAR_CODING or __AD7791_BIPOLAR_CODING """
        outb = bytearray(2)
        outb[0] = __AD7791_MODE_REG + __AD7791_WRITE_OP + __AD7791_CHANSEL_AIN
        outb[1] = __AD7791_CONTINUOUS_CONVERSION_MODE + \
                  __AD7791_BURNOUT_CURRENT_DISABLE + \
                  coding + \
                  __AD7791_BUFFER_ENABLE
        self._spi.write(outb)
        self._conversion_mode = __AD7791_CONTINUOUS

    def start_continuous_conversion(self):
        """writes Mode Register for continuous normal AIN(+)-AIN(-) conversion"""
        outb = bytearray(1)
        outb[0] = __AD7791_DATA_REG + __AD7791_READ_OP + \
                  __AD7791_CONTINUOUS_READ + __AD7791_CHANSEL_AIN
        self._spi.write(outb)
        self._conversion_mode = __AD7791_CONTINUOUS

    def read_raw(self):
        """returns raw read data"""
        # skip writing to communications register when in continuous mode
        # but write to communications register first when in single conversion mode:
        if self._conversion_mode == __AD7791_SINGLE:
            outb = bytearray(1)
            outb[0] = __AD7791_DATA_REG + __AD7791_READ_OP
            self._spi.write(outb)
        inb = bytearray(3)
        self._spi.readinto(inb)
        return inb
    
    def read_unipolar_ADC_voltage(self):
        """returns unipolar ADC voltage referred to Vref"""
        inb = self.read_raw()
        adcval = 65536.0*inb[0] + 256.0*inb[1] + inb[2]
        adcvoltage = adcval/0x1000000*self._ref_voltage
        return adcvoltage
    
    def read_bipolar_ADC_voltage(self):
        """returns bipolar ADC voltage referred to Vref"""
        inb = self.read_raw()
        adcval = 65536.0*inb[0] + 256.0*inb[1] + inb[2]
        adcvoltage = (adcval/0x800000-1.0)*self._ref_voltage
        return adcvoltage
    
if __name__ == "__main__":
    # Hello World!
    from machine import Pin, SPI
    import time
    
    nRDY = Pin(4)
    spi = SPI(0, baudrate=100000, polarity=1, phase=1, bits=8,\
          firstbit=SPI.MSB, sck=Pin(6), mosi=Pin(7), miso=nRDY)
    adc = AD7791(spi, nRDY, ref_voltage=2.5)
    
    print("ref voltage: ", adc.ref_voltage)
    adc.ref_voltage = 6
    adc.ref_voltage = -1
    adc.refvoltage = 2.5
    print("ref voltage: ", adc.ref_voltage)
    print("nRDY: ", adc.nRDY, "value: ", adc.nRDY.value() )
    
    
    print("ADC reset + read status register, power-on value should be 0x8c: ", end="")
    adc.reset()
    status = adc.read_status()
    print(hex(status[0]))
    print("read mode register, power-on value should be 0x02: ", end="")
    mode = adc.read_mode()
    print(hex(mode[0]))
    print("read filter register, power-on value should be 0x04: ", end="")
    filter = adc.read_filter()
    print(hex(filter[0]))

    print("read status register:")
    status = adc.read_status()
    adc.print_status(status[0])
    print("read mode register:")
    mode = adc.read_mode()
    adc.print_mode(mode[0])
    
    print("set filter to CDIV1, 16.6sps:")
    adc.write_filter("CDIV1", "16.6sps")
    filter = adc.read_filter()
    adc.print_filter(filter[0])

    print("start unipolar single conversions:")
    maxtries = 2000
    for conv in range(10):
        ctr=0
        adc.start_unipolar_single_conversion()
        for i in range(maxtries):
            time.sleep_ms(1);
            ctr+=1
            if(adc.nRDY.value() == 0):
                break
        if ctr < maxtries:
            print("Conversion #", conv, " ", end="")
            print("ctr = ", ctr, "rdy = ", adc.nRDY.value(), " ", end="");
            v = adc.read_unipolar_ADC_voltage()
            print("ADC voltage: ", v )
        else:
            print("timeout")

    print("set filter to CDIV8, 9.5sps:")
    adc.write_filter("CDIV8", "9.5sps")
    filter = adc.read_filter()
    adc.print_filter(filter[0])

    print("set coding to unipolar and start continuous conversion:")
    adc.set_coding(__AD7791_UNIPOLAR_CODING)
    adc.start_continuous_conversion()
    maxtries = 1000
    for conv in range(10):
        ctr = 0
        for i in range(maxtries):
            time.sleep_ms(1);
            ctr+=1
            if(adc.nRDY.value() == 0):
                break
        if ctr < maxtries:
            print("Conversion #", conv, " ", end="")
            print("ctr = ", ctr, "rdy = ", adc.nRDY.value(), " ", end="");
            v = adc.read_unipolar_ADC_voltage()
            print("ADC voltage: ", v )
        else:
            print("timeout")