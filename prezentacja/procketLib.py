'''
Library for Procket operations for RFW.
Requires NI driver installation
Requires pyBitBang.py and niDAQlib.py in same folder
'''
import PyBitBang
import NiDAQlib
from robot.api import logger
from time import sleep
import platform


POWER_OUTPUTS2 = {'+24V_ENABLE':0xFE,
                  '+5V_ENABLE':0xFD,
                  '+3V3_ENABLE':0xFB,
                  '+1V8_ENABLE':0xF7,
                  'OUTPUT_LVLSHFT_EN':0xEF,
                  'ALL':0xE0}

POWER_OUTPUTS4 = {'OPTO1_CTRL':0xFE,
                  'OPTO2_CTRL':0xFD,
                  'OPTO3_CTRL':0xFB,
                  'OPTO4_CTRL':0xF7,
                  'RS-232_EN':0xEF,
                  'PROGRAMMER_EN':0xDF,
                  'DUT_PWR1_EN':0xBF,
                  'DUT_PWR2_EN':0x7F,
                  'ALL':0x0}

CONNECTOR_PINS = {'X120-1':0xFE,
                  'X120-2':0xFD,
                  'X120-3':0xFB,
                  'X120-4':0xF7,
                  'X120-ALL':0xF0,
                  'X121-1':0xEF,
                  'X121-2':0xDF,
                  'X121-3':0xBF,
                  'X121-4':0x7F,
                  'X121-ALL':0xF,
                  'ALL':0x0}

GENERAL_PURPOSE_RELAYS = {'EXP0_A76_0':0xFE,
                          'EXP0_A76_1':0xFD,
                          'EXP0_A76_2':0xFB,
                          'EXP0_A76_3':0xF7,
                          'EXP0_A76_4':0xF0,
                          'EXP0_A76_5':0xEF,
                          'EXP0_A76_6':0xDF,
                          'EXP0_A76_7':0xBF,
                          'ALL':0x0}

POWER_STATUS = {'+5V':0x20,
                '+15V':0x10,
                '-15V':0x8,
                '+1V8':0x4,
                '+3V3':0x2,
                '+5VA':0x1,
                'SUPPLIES_OK':0x40}

ANALOG_IO_PINS = {'DAQ_AI0':0xFE,
                  'DAQ_AI4':0xFD,
                  'DAQ_AI1':0xFB,
                  'DAQ_AI5':0xF7,
                  'DAQ_AI2':0xF0,
                  'DAQ_AI6':0xEF,
                  'DAQ_AI3':0xDF,
                  'DAQ_AI7':0xBF}

class procketLib(object):

    '''
    Robot library for easy RFW access
    '''
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '0.1'


    def __init__(self, indev='Dev2'):
        '''
        Library initialization routines
        in      indev = devname on which DAQ is defined in system e.g Dev2
        '''
        self.bitbang = PyBitBang.PyBitBang()
        self.dev = indev
        self.sdaw = '{}/port1/line2'.format(self.dev)
        self.sdar = '{}/port1/line3'.format(self.dev)
        self.scl = '{}/port1/line0'.format(self.dev)
        self.powers2 = 0xFF
        self.powers4 = 0xFF
        self.lines1 = 0xFF
        self.lines3 = 0xFF



    def power_up(self, expander_id, *targets):
        '''
        Powering up board outputs and dut
        in      expander_id = Id of IO expander defined in Procket schema
                targets = 1...8 power outputs to enable, use same names as in Procket schema
        '''
        if int(expander_id) == 2:
            address = 0x44
            curr_setting = self.powers2
            lines = POWER_OUTPUTS2
        elif int(expander_id) == 4:
            address = 0x48
            curr_setting = self.powers4
            lines = POWER_OUTPUTS4
        else:
            raise ValueError('Invalid IO expander id {}'.format(expander_id))
        new_setting = curr_setting
        for target in targets:
            if target in lines:
                value = lines.get(target)
                new_setting = new_setting & value
            else:
                logger.warn('Attempt to use nonexistent output {} on expander {}'
                            .format(target, expander_id))
        if new_setting != curr_setting:
            self.bitbang.i2c_connect(self.sdaw, self.sdar, self.scl)
            self.bitbang.i2c_start()
            self.bitbang.i2c_send(address)
            self.bitbang.i2c_send(new_setting)
            self.bitbang.i2c_stop()
            self.bitbang.i2c_disconnect()
            if int(expander_id) == 2:
                self.powers2 = new_setting
            elif int(expander_id) == 4:
                self.powers4 = new_setting



    def power_down(self, expander_id, *targets):
        '''
        Powering down board outputs and dut
        in      expander_id = Id of IO expander defined in Procket schema
                targets = 1...8 power outputs to disable, use same names as in Procket schema
        '''
        if int(expander_id) == 2:
            address = 0x44
            curr_setting = self.powers2
            lines = POWER_OUTPUTS2
        elif int(expander_id) == 4:
            address = 0x48
            curr_setting = self.powers4
            lines = POWER_OUTPUTS4
        else:
            raise ValueError('Invalid IO expander id {}'.format(expander_id))
        new_setting = curr_setting
        for target in targets:
            if target in lines:
                value = lines.get(target)
                new_setting = new_setting | (value ^ 0xFF)
            else:
                logger.warn('Attempt to use nonexistent output {} on expander {}'
                            .format(target, expander_id))
        if new_setting != curr_setting:
            self.bitbang.i2c_connect(self.sdaw, self.sdar, self.scl)
            self.bitbang.i2c_start()
            self.bitbang.i2c_send(address)
            self.bitbang.i2c_send(new_setting)
            self.bitbang.i2c_stop()
            self.bitbang.i2c_disconnect()
            if int(expander_id) == 2:
                self.powers2 = new_setting
            elif int(expander_id) == 4:
                self.powers4 = new_setting

    def set_connector_pins(self, expander_id, *targets):
        '''
        Setting of X120 & X121 connector pins
        in      expander_id = Id of IO expander defined in Procket schema
                targets = 1...8 outputs to enable, use same names as in Procket schema
        '''
        if int(expander_id) == 1:
            address = 0x72
            curr_setting = self.lines1
            lines = CONNECTOR_PINS
        else:
            raise ValueError('Invalid IO expander id {}'.format(expander_id))
        new_setting = curr_setting
        for target in targets:
            if target in lines:
                value = lines.get(target)
                new_setting = new_setting & value
            else:
                logger.warn('Attempt to use nonexistent output {} on expander {}'
                            .format(target, expander_id))
        if new_setting != curr_setting:
            self.bitbang.i2c_connect(self.sdaw, self.sdar, self.scl)
            self.bitbang.i2c_start()
            self.bitbang.i2c_send(address)
            self.bitbang.i2c_send(new_setting)
            self.bitbang.i2c_stop()
            self.bitbang.i2c_disconnect()
            if int(expander_id) == 1:
                self.lines1 = new_setting

    def reset_connector_pins(self, expander_id, *targets):
        '''
        Resetting of X120 & X121 connector pins
        in      expander_id = Id of IO expander defined in Procket schema
                targets = 1...8 outputs to enable, use same names as in Procket schema
        '''
        if int(expander_id) == 1:
            address = 0x72
            curr_setting = self.lines1
            lines = CONNECTOR_PINS
        else:
            raise ValueError('Invalid IO expander id {}'.format(expander_id))
        new_setting = curr_setting
        for target in targets:
            if target in lines:
                value = lines.get(target)
                new_setting = new_setting | (value ^ 0xFF)
            else:
                logger.warn('Attempt to use nonexistent output {} on expander {}'
                            .format(target, expander_id))
        if new_setting != curr_setting:
            self.bitbang.i2c_connect(self.sdaw, self.sdar, self.scl)
            self.bitbang.i2c_start()
            self.bitbang.i2c_send(address)
            self.bitbang.i2c_send(new_setting)
            self.bitbang.i2c_stop()
            self.bitbang.i2c_disconnect()
            if int(expander_id) == 1:
                self.lines1 = new_setting

    def set_general_purpose_relays(self, expander_id, *targets):
        '''
        Setting of general purpose relays
        in      ExpanderId = Id of IO expander defined in Procket schema
                targets = 1...8 outputs to enable, use same names as in Procket schema
        '''
        if int(expander_id) == 3:
            address = 0x76
            curr_setting = self.lines3
            lines = GENERAL_PURPOSE_RELAYS
        else:
            raise ValueError('Invalid IO expander id {}'.format(expander_id))
        new_setting = curr_setting
        for target in targets:
            if target in lines:
                value = lines.get(target)
                new_setting = new_setting & value
            else:
                logger.warn('Attempt to use nonexistent output {} on expander {}'
                            .format(target, expander_id))
        if new_setting != curr_setting:
            self.bitbang.i2c_connect(self.sdaw, self.sdar, self.scl)
            self.bitbang.i2c_start()
            self.bitbang.i2c_send(address)
            self.bitbang.i2c_send(new_setting)
            self.bitbang.i2c_stop()
            self.bitbang.i2c_disconnect()
            if int(expander_id) == 3:
                self.lines3 = new_setting

    def reset_general_purpose_relays(self, expander_id, *targets):
        '''
        Resetting of general purpose relays
        in      ExpanderId = Id of IO expander defined in Procket schema
                targets = 1...8 outputs to enable, use same names as in Procket schema
        '''
        if int(expander_id) == 3:
            address = 0x76
            curr_setting = self.lines3
            lines = GENERAL_PURPOSE_RELAYS
        else:
            raise ValueError('Invalid IO expander id {}'.format(expander_id))
        new_setting = curr_setting
        for target in targets:
            if target in lines:
                value = lines.get(target)
                new_setting = new_setting | (value ^ 0xFF)
            else:
                logger.warn('Attempt to use nonexistent output {} on expander {}'
                            .format(target, expander_id))
        if new_setting != curr_setting:
            self.bitbang.i2c_connect(self.sdaw, self.sdar, self.scl)
            self.bitbang.i2c_start()
            self.bitbang.i2c_send(address)
            self.bitbang.i2c_send(new_setting)
            self.bitbang.i2c_stop()
            self.bitbang.i2c_disconnect()
            if int(expander_id) == 3:
                self.lines3 = new_setting

    def read_connector_pins(self, expander_id):
        '''
        Reading of X122 & X123 connector pins
        in      expander_id = Id of IO expander defined in Procket schema
        '''
        if int(expander_id) == 2:
            address = 0x75
        else:
            raise ValueError('Invalid IO expander id {}'.format(expander_id))
        self.bitbang.i2c_connect(self.sdaw, self.sdar, self.scl)
        self.bitbang.i2c_start()
        self.bitbang.i2c_send(address)
        data = self.bitbang.i2c_receive()
        self.bitbang.i2c_stop()
        self.bitbang.i2c_disconnect()
        return data

    def log_power_status(self):
        '''
        Writes status of power lines to log
        '''
        address = 0x43
        self.bitbang.i2c_connect(self.sdaw, self.sdar, self.scl)
        self.bitbang.i2c_start()
        self.bitbang.i2c_send(address)
        status = self.bitbang.i2c_receive()
        self.bitbang.i2c_stop()
        self.bitbang.i2c_disconnect()
        #logger.info("Power status: {}".format(status))
        keys = list(POWER_STATUS.keys())
        logger.info('Powers ON:')
        for key in keys:
            if POWER_STATUS.get(key) & status:
                logger.info('{}'.format(key))

    def write_do(self, data, port='0', line=None):
        '''
        Writing digital output port or line
        in      data = byte to write, in case of single line 0/1
                port = DO port to write, 0 by default
                line = DO line to write, None by default, define a value 0...7
                       when setting only one line
        '''
        data = int(data)
	
        logger.info("testlog, Indata: {}".format(data))	 
        if line:
            daq = NiDAQlib.connect_do_line('{}/{}/{}'.format(self.dev, port, line))
        else:
            daq = NiDAQlib.connect_do_port('{}/{}'.format(self.dev, port))
        NiDAQlib.write_do(daq, data)
        NiDAQlib.disconnect(daq)

    def read_di(self, port='0', line=None):
        '''
        Reading digital input port or line
        in      port = DO port to read, 0 by default
                line = DO line to read, None by default, define a value 0...7
                       when reading only one line
        out     data = read data
        '''
        if line:
            daq = NiDAQlib.connect_di_line('{}/{}/{}'.format(self.dev, port, line))
        else:
            daq = NiDAQlib.connect_di_port('{}/{}'.format(self.dev, port))
        data = NiDAQlib.read_di(daq)
        NiDAQlib.disconnect(daq)
		#sleep(0.1)
        logger.info("DI data: {}".format(data))
		

    def read_analog_io_RSE(self, port='ai2', samples=2, rate=100.0):
        '''
        Reading analog input port, referenced single-ended (RSE)
        in      port = AI port to read, 2 by default
                samples = The number of samples, per channel, to read. 2 by default.
                     
        out     data = read data
        '''
        daq = NiDAQlib.connect_analog_io_port_RSE('{}/{}'.format(self.dev, port), int(samples), float(rate))
        data = NiDAQlib.read_analog_io_RSE(daq, int(samples))
        NiDAQlib.disconnect(daq)
        return data
    
    def read_analog_io_Diff(self, port1='ai2', samples=2, rate=100.0):
        '''
        Reading analog input port, differential mode (DIFF)
        in      port = AI port to read, 2 by default
                samples = The number of samples, per channel, to read. 2 by default.
                      
        out     data = read data
        '''
        daq = NiDAQlib.connect_analog_io_port_Diff('{}/{}'.format(self.dev, port1), int(samples), float(rate))
        data = NiDAQlib.read_analog_io_Diff(daq, int(samples))
        NiDAQlib.disconnect(daq)
        return data
         
        
    def procket_up(self):
        '''
        Procket powerup init function for Suite Setup
        '''
        addresses = [0x44, 0x48]
        self.bitbang.i2c_connect(self.sdaw, self.sdar, self.scl)
        for address in addresses:
            self.bitbang.i2c_start()
            self.bitbang.i2c_send(address)
            self.bitbang.i2c_send(0xFF)
            self.bitbang.i2c_stop()
        self.bitbang.i2c_start()
        self.bitbang.i2c_send(0x44)
        self.bitbang.i2c_send(0xFE)
        self.bitbang.i2c_stop()
        self.bitbang.i2c_disconnect()
        self.powers2 = 0xFE

    def procket_down(self):
        '''
        Procket powerdown function for Suite Teardown
        '''
        addresses = [0x44, 0x48]
        self.bitbang.i2c_connect(self.sdaw, self.sdar, self.scl)
        for address in addresses:
            self.bitbang.i2c_start()
            self.bitbang.i2c_send(address)
            self.bitbang.i2c_send(0xFF)
            self.bitbang.i2c_stop()
        self.bitbang.i2c_disconnect()

    def readmemory(self):
        '''
        Reading data from specific index in 2Kbit memory
        out     index = 1-10 by default
        '''
        self.bitbang.i2c_connect(self.sdaw, self.sdar, self.scl)
        for index in range(1, 10):
            self.bitbang.i2c_start()
            self.bitbang.i2c_send(0xA0)
            self.bitbang.i2c_send(index)    #index
            self.bitbang.i2c_start()
            self.bitbang.i2c_send(0xA1)
            data  = self.bitbang.i2c_receive()	 
            self.bitbang.i2c_stop()
            logger.info("Value in index {} is {}".format(index, data))
        self.bitbang.i2c_disconnect()
        return data


    def writememory(self, index='1', dataByte='1'):
        '''
        Writing data to specific index in 2Kbit memory (address is A0).
        in      index = 1 by default
                data = 1 by default
        '''
        self.bitbang.i2c_connect(self.sdaw, self.sdar, self.scl)
        self.bitbang.i2c_start()
        self.bitbang.i2c_send(0xA0)
        self.bitbang.i2c_send(int(index))    #index
        self.bitbang.i2c_send(int(dataByte))    #dataByte
        logger.info("Write value {} to index {}".format(dataByte, index))
        self.bitbang.i2c_stop()
        self.bitbang.i2c_disconnect()


    def write_analog_io(self, port='ao0', value='5'):
        '''
        Writing voltage value (By default 5V) to analog output port
        in      port = AO port to read, 0 by default
                value = Voltage value, 5V by default
        out     data = write data
        '''
        daq = NiDAQlib.connect_analog_write_io_port('{}/{}'.format(self.dev, port))
        data = NiDAQlib.write_analog_io(daq, value)
        NiDAQlib.disconnect(daq)
        return data

    
    def trigger_analog_input(self, port='ai2', samples=2, rate=100.0, edge_selection='R'):
        '''
        Using PFI to Trigger an Analog Input Acquisition
        in      port = AI port to read, 2 by default
                edge_selection = Rising by default
        out     data = read data
        '''
        daq = NiDAQlib.trigger_analog_input('{}/{}'.format(self.dev, port), int(samples), float(rate), edge_selection)
        data = NiDAQlib.read_analog_io_Diff(daq, int(samples))
        NiDAQlib.disconnect(daq)
        return data
    
    def trigger_analog_output(self, port='ao1', value='1', edge_selection='R'):
        '''
        Using PFI to Trigger an Analog Output Generation
        in      port = AO port to read, 1 by default
                value = value = Voltage value, 5V by default
                edge_selection = Rising by default
        out     data = read data
        '''
        daq = NiDAQlib.trigger_analog_output('{}/{}'.format(self.dev, port), edge_selection)
        data = NiDAQlib.write_analog_io_trigger(daq, value)
        NiDAQlib.disconnect(daq)
        return data  

    def counter(self, port='ctr0', edge_selection='R', initialCount=0, delayInReadCounter=1.0):
        '''
        Using PFI1 as a Counter Source
        in      port = ctr0 port to read 
                initialCount = 0 by default
                edge_selection = Rising by default
                delayInReadCounter = 1sec by default
        out     data = read data
        '''
        daq = NiDAQlib.counter_setup('{}/{}'.format(self.dev, port), edge_selection, int(initialCount))
        data = NiDAQlib.counter_read(daq, float(delayInReadCounter))
        NiDAQlib.disconnect(daq)
        return data  

    def python_version(self):
        '''
        Prints used Python version
        '''
        logger.info("testlog, python version is {}".format(platform.python_version()))           
        