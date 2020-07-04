"""
Enphase2Emon will receive the /stream/meter chunked http stream from an 
Enphase Envoy s and transfer the data to EmonCMS running locally.


Enphase2Emon.py is the core program.

Also uses
ReceiveEnphaseStream.py
WriteToEmoncmsHTTP.py
"""

__version__ = "0.0.7"
__author__ = "SWW"

# In Daemon form, this must be given the full path. 
CONFIG_FILE = '/home/pi/Enphase2emon/Enphase2Emon.cfg'

# Local Files
import ReceiveEnphaseStream
import WriteToEmoncmsHTTP


import json
import configparser
import time
import signal
import sys

import logging
from systemd.journal import JournalHandler as systemdJournalHandler

# Program Flow
# Read config file
# Open stream URL with authentication
#  On fail try again every 60 sec
#  On lost stream reattempt every 60
# Receive data from stream 
# Check formatting
# Check timing only update ever interval seconds
# yield
# Receive yield and communicate to emon

# Switch to Python Daemon
# Catch Exceptions
# Notice a lost stream





# TODO use try except
def MainLoop():
    #Setup Loging
    LG = logging.getLogger('Enphase2Emon')
    
    #Scream.dbg('MainLoop','Have Screamer')
    
    config = configparser.ConfigParser()
    #Scream.dbg('MainLoop','Have configparser')
    
    # ConfigParser.read "Files that cannot be opened are silently ignored;       
    # Return list of successfully read files.\n        "
    ListOfRead = config.read(CONFIG_FILE)
    #Scream.dbg('MainLoop','config.read found {}'.format(ListOfRead))
    
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
        
    
        
    LGformatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Are we logging to a file
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
    
    # Signal Handeler
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
        if SoftKillReceived:
            LG.info('Executing signalNumber: {}'.format(SignalNumReceived))
            LG.info('EXITING')
            sys.exit(0)

    # print(config['Envoy']['ipadd'])
    # print(type(config['Envoy']['ipadd']))
    # print(config['Settings']['updateinterval'])
    # print(type(config['Settings'].getint('updateinterval')))
    # print(config['Settings']['smoothing'])
    # print(type(config['Settings'].getboolean('smoothing')))

    StripPrefix = config['Envoy'].getint('num_chars_strip')
    LG.debug('MainLoop StripPrefix {}'.format(StripPrefix))

    PostInter = config['Settings'].getint('UpdateInterval')
    LG.debug('MainLoop PostInter {}'.format(PostInter))

    # Setup the object to post to emoncms
    poster = WriteToEmoncmsHTTP.EMONPostHTTP(CONFIG_FILE)
    LG.debug('MainLoop poster ready')

    TimeLast = time.time()
    LG.debug('MainLoop TimeLast {}'.format(TimeLast))
    
    GracefulExitCheck()
    
    # Loop over stream
    for LineIn in ReceiveEnphaseStream.DataStream(config['Envoy']['ipadd'],
                                                    config['Envoy']['path'],
                                                    config['Envoy']['userid'],
                                                    config['Envoy']['userpass']):
        
        GracefulExitCheck()
        
        LG.debug('MainLoop LineIn received')
        
        # The output has initial characters that need to be striped. Thus StripPrefix
        LineDict = json.loads(LineIn.decode("utf-8")[StripPrefix:])
        LG.debug('MainLoop LineDict decoded')
        
        GracefulExitCheck()
        
        if (time.time() - TimeLast) > PostInter:
            LG.debug('MainLoop time good - posting')
            poster.PostToEMON(LineDict)
            TimeLast = time.time()
        
        GracefulExitCheck()
        
            
            

if __name__ == "__main__":
    print("Running Enphase2Emon as __main__")
    MainLoop()
    
#configparser.ConfigParser.read.__doc__
#"Read and parse a filename or an iterable of filenames.\n\n

# Files that cannot be opened are silently ignored; this is\n        
# designed so that you can specify an iterable of potential\n        
# configuration file locations (e.g. current directory, user's\n        
# home directory, systemwide directory), and all existing\n        
# configuration files in the iterable will be read.  A single\n        
# filename may also be given.\n\n        
# Return list of successfully read files.\n        "
