'''
Library for i2c bitbanging in Procket environment.
Can be used in any simple, one master setup

Example:
    DAQ = pyBitBang() #Create object
    DAQ.i2c_connect(SDAwrite='Dev1/port1/line2',SDAread='Dev1/port1/line3',
                    SCL='Dev1/port1/line0') #Create tasks
    DAQ.i2c_start() #send i2c start sequence
    DAQ.i2c_send(0x44) #send receiver address
    DAQ.i2c_send(0x12) #send payload data
    DAQ.i2c_stop() #send i2c stop sequence
    DAQ.i2c_disconnect() #release resources
'''
from NiDAQlib import connect_do_line, connect_di_line, disconnect, write_do, read_di
#from robot.api import logger

#Note! Inverted signals for procket inverted output lines
HIGH = 0
LOW = 0xFF

class PyBitBang(object):

    '''
    Robot library for easy RFW access
    '''
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '0.1'

    def __init__(self):
        self.write_sda = None
        self.read_sda = None
        self.write_scl = None


    def i2c_connect(self, sda_write='Dev2/port1/line2', sda_read='Dev2/port1/line3',
                    scl='Dev2/port1/line0'):
        '''
        Task creation for SDA write, read and SCL signal
        in      SDAwrite = dev/port/line pin for SDA write line, default 'Dev2/port1/line2'
                SDAread = dev/port/line pin for SDA read line, default 'Dev2/port1/line3'
                SCL = dev/port/line pin SCL line, default 'Dev2/port1/line0'
        '''
        self.write_sda = connect_do_line(sda_write)
        self.read_sda = connect_di_line(sda_read)
        self.write_scl = connect_do_line(scl)

    def i2c_disconnect(self):
        '''
        Stop and clear all i2c tasks
        '''
        disconnect(self.write_sda)
        disconnect(self.read_sda)
        disconnect(self.write_scl)


    def set_sda(self, value):
        '''
        Set SDA to given state
        in      value = value to set (HIGH or LOW)
        '''
        write_do(self.write_sda, value)

    def set_scl(self, value):
        '''
        Set SCL to given state
        in      value = value to set (HIGH or LOW)
        '''
        write_do(self.write_scl, value)

    def get_sda(self):
        '''
        Get SDA state
        out      retval = value read from SDA 0 or 1
        '''
        retval = read_di(self.read_sda)
        #logger.info('GetSDA returning {}'.format(retval))
        return retval

    def i2c_start(self):
        '''
        Write i2c start sequence to lines
        '''
        self.set_sda(HIGH)
        self.set_scl(HIGH)
        self.set_sda(LOW)
        self.set_scl(LOW)


    def i2c_stop(self):
        '''
        Write i2c stop sequence to lines
        '''
        self.set_sda(LOW)
        self.set_scl(HIGH)
        self.set_sda(HIGH)

    def i2c_send(self, data):
        '''
        Sends given byte to line bit by bit, verifies ACKs, raises ValueError in case of failed ACK
        in      data = byte to send
        '''
        for _ in range(8):
            if data & 0x80:
                self.set_sda(HIGH)
            else:
                self.set_sda(LOW)
            self.set_scl(HIGH)
            self.set_scl(LOW)
            data = data<<1

        self.set_sda(HIGH)
        self.set_scl(HIGH)
        if self.get_sda() != 0:
            raise ValueError('Receiver nacked sent data')
        self.set_scl(LOW)

    def i2c_receive(self):
        '''
        Receives byte from line bit by bit
        out      data = received byte
        '''
        data = 0x0
        for _ in range(8):
            data = data<<1
            self.set_scl(HIGH)
            if self.get_sda() != 0:
                data = data | 1
            self.set_scl(LOW)
        self.set_sda(HIGH)
        self.set_scl(HIGH)
        self.set_scl(LOW)

        return data
