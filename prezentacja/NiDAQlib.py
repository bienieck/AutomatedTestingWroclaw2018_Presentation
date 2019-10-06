'''
Library for niDAQ operations.
Requires PyDAQmx (https://pythonhosted.org/PyDAQmx/) and
NI driver installation
'''


from PyDAQmx import Task
import ctypes
import PyDAQmx.DAQmxFunctions
from PyDAQmx.DAQmxFunctions import DAQError
from  PyDAQmx.DAQmxConstants import *
from PyDAQmx.DAQmxTypes import uInt8, int32, bool32, float64, uInt32, byref, uInt64
from robot.api import logger
from time import sleep

def connect_do_port(devport):
    '''
    Initialize task for writing to digital output port
    in    Device/port e.g. Dev1/port0
    out   Task handle
    '''
    task = Task()
    task.CreateDOChan(devport, '', DAQmx_Val_ChanForAllLines)
    task.StartTask()
    return task

def connect_do_line(devportline):
    '''
    Initialize task for writing to digital output lines
    in      Device/port/lines e.g. Dev1/port0/line0:3
            also single line supported e.g. Dev1/port0/line1
    out     Task handle
    '''
    task = Task()
    task.CreateDOChan(devportline, '', DAQmx_Val_ChanPerLine)
    task.StartTask()
    return task

def connect_di_port(devport):
    '''
    Initialize task for reading from digital input port
    in    devport = Device/port e.g. Dev1/port0
    out   task = Task handle
    '''
    task = Task()
    task.CreateDIChan(devport, '', DAQmx_Val_ChanForAllLines)
    task.StartTask()
    return task

def connect_di_line(devportline):
    '''
    Initialize task for reading from digital input lines
    in      devportline = Device/port/lines e.g. Dev1/port0/line0:3
                          also single line supported e.g. Dev1/port0/line1
    out     task = Task handle
    '''
    task = Task()
    task.CreateDIChan(devportline, '', DAQmx_Val_ChanPerLine)
    task.StartTask()
    return task

def write_do(taskhandle, indata, intimeout=0):
    '''
    Write given data to given task
    in      taskhandle = Task handle
            indata = Samples to write as list of integers
            intimeout = Timeout for writing all samples, default 0 = try once

    out     ErrorText = Error text, None if no errors
    '''
    errortext = None
	#logger.info("Indata: {}".format(indata))
    if isinstance(indata, int):
        samplecount = 1
        datatype = uInt8
        data = datatype(indata)
    else:
        samplecount = len(indata)
        datatype = uInt8*samplecount
        data = datatype(*indata)
    result = int32()
    samples = int32(samplecount)
    autostart = bool32(False)
    timeout = float64(intimeout)
    try:
        taskhandle.WriteDigitalU8(samples, autostart, timeout,
                                  DAQmx_Val_GroupByChannel, data,
                                  byref(result), None)
    except DAQError as err:
        errortext = err
    return errortext

def read_di(taskhandle, intimeout=0):
    '''
    Read data from given task
    in      Task handle
            Timeout for reading, default 0 = try once

    out     Read data
    '''
    value = uInt8()
    result = int32()
    bytespersample = int32()
    samples = int32(1)
    readarraysize = uInt32(1)
    timeout = float64(intimeout)
    taskhandle.ReadDigitalU8(samples, timeout,
                             DAQmx_Val_GroupByScanNumber, value,
                             readarraysize, byref(result), None)
    return value.value

def disconnect(taskhandle):
    '''
    Stops and clears given task
    '''
    taskhandle.StopTask()
    taskhandle.ClearTask()


#connect and read analog port, Differential mode 
def connect_analog_io_port_Diff(devport, samples, rate):
    '''
    Initialize task for reading from analog input port for Voltage measurement
    in    devport = Device/port e.g. Dev1/port0
    out   task = Task handle
    '''
    logger.info("temp: {}".format(devport))
    max_num_samples = samples
    task = Task()
    task.CreateAIVoltageChan(devport, '', DAQmx_Val_Diff, -10.0, 10.0, DAQmx_Val_Volts, None)
    task.CfgSampClkTiming('', float64(rate), DAQmx_Val_Rising,
                          DAQmx_Val_FiniteSamps, uInt64(max_num_samples))    
    task.StartTask()
    return task
def read_analog_io_Diff(taskhandle, samples, intimeout=100):
    '''
    Read data from given task
    in      Task handle
            Timeout for reading, default 100
    out     Read data
    '''
    datatype = ctypes.c_double*samples
    data = datatype()  
    result = int32()
    readarraysize = uInt32(samples * 2) 
    timeout = float64(intimeout)    
    taskhandle.ReadAnalogF64(samples, timeout,
                             DAQmx_Val_GroupByChannel, data,
                             readarraysize, byref(result), None)
    #sleep(0.1)
    for i in data:
        logger.info("Voltage level: {}".format(str(i)))
    return repr(data)

#connect and read analog port, Referenced Single-Ended mode    
def connect_analog_io_port_RSE(devport, samples, rate):
    '''
    Initialize task for reading from analog input port for Voltage measurement
    in    devport = Device/port e.g. Dev1/ai2
    out   task = Task handle
    '''
    logger.info("temp: {}".format(devport))
    max_num_samples = samples
    task = Task()
    task.CreateAIVoltageChan(devport, '', DAQmx_Val_RSE, -10.0, 10.0, DAQmx_Val_Volts, None)
    task.CfgSampClkTiming('', float64(rate), DAQmx_Val_Rising,
                          DAQmx_Val_FiniteSamps, uInt64(max_num_samples))    
    task.StartTask()
    return task
def read_analog_io_RSE(taskhandle, samples, intimeout=100):
    '''
    Initialize task for reading from analog input port for Voltage measurement
    in    devport = Device/port e.g. Dev1/ai2
          Timeout for reading, default 100
    out   task = Task handle
    '''
    datatype = ctypes.c_double*samples
    data = datatype()  
    result = int32()
    readarraysize = uInt32(samples)
    timeout = float64(intimeout)    
    taskhandle.ReadAnalogF64(samples, timeout,
                             DAQmx_Val_GroupByChannel, data,
                             readarraysize, byref(result), None)
    #sleep(0.1)
    for i in data:
        logger.info("Voltage level: {}".format(str(i)))
    return repr(data)

#PFI, analog I/O trigger    
def trigger_analog_input(devport, samples, rate, edge_selection):
    '''
    Using PFI to Trigger an Analog Input Acquisition
    in    devport = Device/port e.g. Dev2/PFI0
    out   task = Task handle
    '''
    logger.info("testlog, Device: {}".format(devport))
    max_num_samples = samples
    task = Task()
    task.CreateAIVoltageChan(devport, '', DAQmx_Val_RSE, -10.0, 10.0, DAQmx_Val_Volts, None)
    task.CfgSampClkTiming('', float64(rate), DAQmx_Val_Rising,
                          DAQmx_Val_FiniteSamps, uInt64(max_num_samples))    
    #logger.info("trigger analog input -function, 1: {}")
    if edge_selection == 'R':
        task.CfgDigEdgeStartTrig("/Dev2/PFI0", DAQmx_Val_Rising)
        logger.info("testlog, trigger analog input -function, Rising: {}")
    else:
        task.CfgDigEdgeStartTrig("/Dev2/PFI0", DAQmx_Val_Falling)
        logger.info("testlog, trigger analog input -function, Falling: {}")
    task.StartTask()
    return task 

def trigger_analog_output(devport, edge_selection):
    '''
    Using PFI to Trigger an Analog Output Generation
    in    devport = Device/port e.g. Dev2/PFI0
    out   task = Task handle
    '''
    logger.info("testlog, Device: {}".format(devport))
    max_num_samples = 2
    task = Task()
    task.CreateAOVoltageChan(devport, '', -10.0, 10.0, DAQmx_Val_Volts, None) 
    task.CfgSampClkTiming('', float64(100), DAQmx_Val_Rising,
                          DAQmx_Val_FiniteSamps, uInt64(max_num_samples))        
       
    if edge_selection == 'R':
        task.CfgDigEdgeStartTrig("/Dev2/PFI1", DAQmx_Val_Rising)
        #logger.info("testlog, trigger analog output -function, Rising: {}")
    else:
        task.CfgDigEdgeStartTrig("/Dev2/PFI1", DAQmx_Val_Falling)
        #logger.info("testlog, trigger analog output -function, Falling: {}")
    return task 
  
def write_analog_io_trigger(taskhandle, value, intimeout=100):
    '''
    Write data from given task
    in      Task handle
            Timeout for writing, default 100

    out     write data
    '''
    samples = 2
    datatype = float64*samples
    data = datatype()  
    for i in range(samples):
    
        data[i] = float(value)
        #logger.info("testlog, write analog io trigger -funtion for loop 1: {}".format(value))
    for i in data:
        logger.info("testlog, write analog io trigger -funtion, for loop 2: {}".format(str(i)))
    
    timeout = float64(intimeout)
    #logger.info("write analog io trigger -funtion, test1: {}".format(data))
    taskhandle.WriteAnalogF64(2, False, timeout, DAQmx_Val_GroupByChannel, data, int32(), None)
    
    taskhandle.StartTask()
    taskhandle.WaitUntilTaskDone(-1)
    return data
    
def connect_analog_write_io_port(devport):
    '''
    Initialize task for writing Voltage data to analog output port
    in    devport = Device/port e.g. Dev2/ao0
    out   task = Task handle
    '''
    max_num_samples = 1
    task = Task()
    task.CreateAOVoltageChan(devport, '', -10.0, 10.0, DAQmx_Val_Volts, None)
    task.StartTask()
    return task

def write_analog_io(taskhandle, value, intimeout=100):
    '''
    Write data from given task
    in      Task handle
            Timeout for writing, default 100

    out     write data
    '''
    samples = 1
    data = float(value)
    timeout = float64(intimeout)
    taskhandle.WriteAnalogScalarF64(0, timeout, data, None)
    sleep(0.5)
    logger.info("testlog, write analog io -function, Voltage level: {}".format(data))
    return data

def counter_setup(devport, edge_selection, initialCount):
    '''
    Initialize task for Counter operation
    in      devport
            edge_selection
            initialCount
    '''
    logger.info("testlog, Device: {}".format(devport))
    task = Task()
 
    if edge_selection == 'R':
        task.CreateCICountEdgesChan(devport, '', DAQmx_Val_Rising , initialCount, DAQmx_Val_CountUp ) 
        logger.info("testlog,  Rising Edge selected: {}")
    else:
        task.CreateCICountEdgesChan(devport, '', DAQmx_Val_Falling , initialCount, DAQmx_Val_CountUp ) 
        logger.info("testlog,  Falling Edge selected: {}")
      
    task.StartTask() 
    logger.info("testlog, initialCount given in CreateCICountEdgesChan {}".format(initialCount))
    return task 

def counter_read(taskhandle, delayInReadCounter):
    '''
    Read counter values
    in      taskhandle
            delayInReadCounter
             
    '''
    datatype = ctypes.c_uint
    data = datatype()
           
    logger.info("testlog, readCounter before startTask: {}".format(data.value))
    
    #with the default parameters counter values are printed out 10 times (once in a second). 
    #Modify value in for-loop and delayInReadCounter-parameter if needed.
    for counter in range(1,11):
        taskhandle.ReadCounterScalarU32(-1, data, None)
        logger.info("testlog, readcounter after StartTask (in for-loop): {}".format(data.value))
        sleep(delayInReadCounter)
       
    logger.info("testlog, final ReadCounter value {}".format(data.value))
    return data
     

