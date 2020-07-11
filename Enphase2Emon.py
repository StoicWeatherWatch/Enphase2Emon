"""
Enphase2Emon will receive the /stream/meter chunked http stream from an 
Enphase Envoy s and transfer the data to EmonCMS running locally. It is designed to run
as a daemon on the same R Pi as EmonCMS but it will happily run on a different 
linux box.


Enphase2Emon.py is the core.

Also uses
ReceiveEnphaseStream.py
WriteToEmoncmsHTTP.py

Config file expected. 

Requires 
requests
systemd-python - Used for logging. 
                    To remove this requirement, 
                    remove the systemd journal logging handler.)

"""

__version__ = "0.1.0"
__author__ = "SWW"

# In Daemon form, this must be given the full path. 
CONFIG_FILE = '/home/pi/Enphase2Emon/Enphase2Emon.cfg'

# Local Files
import ReceiveEnphaseStream
import WriteToEmoncmsHTTP


import json
import configparser
import time
import signal
import sys
import traceback
import logging

# Requires pip3 install systemd-python
from systemd.journal import JournalHandler as systemdJournalHandler

# Program Flow
# Read config file and setup logging
# Initial setup
# Open stream URL with authentication
#  On fail exit and daemon service will restart. Maybe.
#  On lost stream exit and daemon service will restart. Maybe.
# Receive data from stream 
# Check formatting - Not yet
# Check timing only update ever interval seconds
# yield
# Receive yield and communicate to emon

# TODO
# Notice a lost stream (Time out in place. Maybe enough)



def MainLoop():
    #Setup Loging
    LG = logging.getLogger('Enphase2Emon')
    
    # Get config file (It has logging settings)
    config = configparser.ConfigParser()
    
    # ConfigParser.read "Files that cannot be opened are silently ignored;       
    # Returns list of successfully read files."
    ListOfRead = config.read(CONFIG_FILE)
    
    # Continue with logging setup
    if config['Logging']['log_level'] == 'DEBUG':
        LogLevel = logging.DEBUG
    elif config['Logging']['log_level'] == 'INFO':
        LogLevel = logging.INFO
    elif config['Logging']['log_level'] == 'WARNING':
        LogLevel = logging.WARNING
    elif config['Logging']['log_level'] == 'CRITICAL':
        LogLevel = logging.CRITICAL
    else:
        # default and if not correct config is ERROR
        LogLevel = logging.ERROR
    
    # What the logs will look like
    LGformatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Are we logging to a file
    if config['Logging']['Log_File']:
        if len(config['Logging']['Log_File']) > 1:
            FLHandler = logging.FileHandler(config['Logging']['Log_File'])
            FLHandler.setLevel(LogLevel)
            FLHandler.setFormatter(LGformatter)
            LG.addHandler(FLHandler)
    
    # Logging to systemd journal
    if config['Logging'].getboolean('Log_To_systemd_journal', fallback=False):
        SJHandler = systemdJournalHandler(level=LogLevel)
        SJHandler.setFormatter(LGformatter)
        LG.addHandler(SJHandler)
        
    # Log nothing if no logger is set
    if not LG.hasHandlers():
        LG.addHandler(logging.NullHandler())
    
    # This line is necessary because we must also set the minimum for the logger overall
    LG.setLevel(LogLevel)
    
    LG.info('Enphase2Emon MainLoop() has started. Logging on and config file loaded')
    LG.debug('config.read found {}'.format(ListOfRead))
    
    #LG.critical(' critical test')
    #LG.error(' error test')
    #LG.warning(' warning test')
    #LG.info(' info test')
    #LG.debug(' debug test')
    #LG.exception(msg, *args, **kwargs)
    
    
    # Signal Handeler - for exiting gracefully on SIGTERM
    SoftKillReceived = False
    SignalNumReceived = 0
    SignalFrameReceived = None
    
    def receiveSIGTERM(signalNumber, frame):
        LG.info('Received signalNumber: {} - Will wait for a good place'.format(signalNumber))
        # nonlocal accesses the variable in the outer scope. In this case MainLoop()
        nonlocal SignalNumReceived
        SignalNumReceived = signalNumber
        nonlocal SignalFrameReceived
        SignalFrameReceived = frame
        nonlocal SoftKillReceived
        SoftKillReceived = True
        
    def receiveSIGINT(signalNumber, frame):
        LG.info('Received signalNumber: {} - Will wait for a good place'.format(signalNumber))
        nonlocal SignalNumReceived
        SignalNumReceived = signalNumber
        nonlocal SignalFrameReceived
        SignalFrameReceived = frame
        nonlocal SoftKillReceived
        SoftKillReceived = True
    
    signal.signal(signal.SIGTERM, receiveSIGTERM)
    signal.signal(signal.SIGINT, receiveSIGINT)
    
    def GracefulExitCheck():
        nonlocal SoftKillReceived
        nonlocal SignalNumReceived
        nonlocal SignalFrameReceived
        if SoftKillReceived:
            LG.info('Executing signalNumber: {}'.format(SignalNumReceived))
            LG.debug('Signal Frame was: {}'.format(SignalFrameReceived))
            LG.info('EXITING')
            sys.exit(0)


    # Finish reading the config file
    StripPrefix = config['Envoy'].getint('num_chars_strip')
    LG.debug('MainLoop StripPrefix {}'.format(StripPrefix))

    PostInter = config['Settings'].getint('UpdateInterval')
    LG.debug('MainLoop PostInter {}'.format(PostInter))
    
    # Used to post only every PostInter seconds
    TimeLast = time.time()
    LG.debug('MainLoop TimeLast {}'.format(TimeLast))


    # Setup the object to post to emoncms
    poster = WriteToEmoncmsHTTP.EMONPostHTTP(CONFIG_FILE)
    LG.debug('MainLoop poster ready')
    
    GracefulExitCheck()
    
    # Loop over stream
    try:
        for LineIn in ReceiveEnphaseStream.DataStream(config['Envoy']['ipadd'],
                                                        config['Envoy']['path'],
                                                        config['Envoy']['userid'],
                                                        config['Envoy']['userpass']):
        
            GracefulExitCheck()
        
            LG.debug('MainLoop LineIn received')
        
            # Turn the received stream chunk text into a python dictionary of data
            try:
                # The output has initial characters that need to be striped. Thus StripPrefix
                LineDict = json.loads(LineIn.decode("utf-8")[StripPrefix:])
                LG.debug('MainLoop LineDict decoded')
            except json.JSONDecodeError as err:
                LG.error('Error decoding line in with JSON. Will quit and hopefully be restarted')
                LG.debug(err.msg)
                LG.debug(err.doc)
                LG.debug(err.pos)
                LG.debug(traceback.format_exc())
                LG.exception(err)
                LG.error('EXITING with error 16')
                sys.exit(16)
        
            GracefulExitCheck()
        
            # Post the data to EmonCMS
            if (time.time() - TimeLast) > PostInter:
                LG.debug('MainLoop time good - posting')
                try:
                    poster.PostToEMON(LineDict)
                except WriteToEmoncmsHTTP.E2EPosterError_Fatal as err:
                    LG.error('Error sending data to EmonCMS. Will quit and hopefully be restarted')
                    LG.debug(err.location)
                    LG.debug(err.message)
                    LG.debug(err)
                    if err.cause.request:
                        LG.debug(err.cause.request)
                    if err.cause.response:
                        LG.debug(err.cause.response)
                    LG.debug(traceback.format_exc())
                    LG.exception(err.cause)
                    #LG.debug(repr(traceback.format_tb(err.cause.tb)))
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    LG.debug(repr(traceback.format_tb(exc_traceback)))
                    LG.error('EXITING with error 17')
                    sys.exit(17)
                
                # Posted successfully, reset the clock 
                TimeLast = time.time()
        
            GracefulExitCheck()
            
    except ReceiveEnphaseStream.E2EReceiveError_Fatal as err:
        LG.error('Error receiving data stream. Will quit and hopefully be restarted')
        LG.debug(err.location)
        LG.debug(err.message)
        LG.debug(err)
        if err.cause.request:
            LG.debug(err.cause.request)
        if err.cause.response:
            LG.debug(err.cause.response)
        LG.debug(traceback.format_exc())
        LG.exception(err.cause)
        #LG.debug(repr(traceback.format_tb(err.cause.tb)))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        LG.debug(repr(traceback.format_tb(exc_traceback)))
        LG.error('EXITING with error 15')
        sys.exit(15)
        
        
    LG.error('Error left infinite loop. Should never reach this point.')
    exc_type, exc_value, exc_traceback = sys.exc_info()
    LG.debug(traceback.format_exc())
    LG.debug(repr(traceback.format_tb(exc_traceback)))
    LG.error('EXITING with error 18')
    # Standard exit codes (These are not)
    # https://freedesktop.org/software/systemd/man/systemd.exec.html#id-1.20.8
    sys.exit(18) 


if __name__ == "__main__":
    print("Running Enphase2Emon as __main__")
    MainLoop()
    

