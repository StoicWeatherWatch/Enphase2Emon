"""
Enphase2Emon will receive the /stream/meter chunked http stream from an 
Enphase Envoy s and transfer the data to EmonCMS running locally.


Enphase2Emon.py is the core program.

Also uses
ReceiveEnphaseStream.py
WriteToEmoncmsHTTP.py
"""

__version__ = "0.0.2"
__author__ = "SWW"

# In Daemon form, this must be given the full path. 
CONFIG_FILE = '/home/pi/Enphase2Emon.cfg'

# Local Files
import ReceiveEnphaseStream
import WriteToEmoncmsHTTP

from Screamer import Screamer


import json
import configparser
import time

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
# Switch prints to log 

# Read config file
# TODO use try except
def MainLoop():
    Scream = Screamer.LocalOnly('Enphase2Emon')
    Scream.dbg('MainLoop','Have Screamer')
    config = configparser.ConfigParser()
    Scream.dbg('MainLoop','Have configparser')
    
    # ConfigParser.read "Files that cannot be opened are silently ignored;       
    # Return list of successfully read files.\n        "
    ListOfRead = config.read(CONFIG_FILE)
    Scream.dbg('MainLoop','config.read found {}'.format(ListOfRead))

    # print(config['Envoy']['ipadd'])
    # print(type(config['Envoy']['ipadd']))
    # print(config['Settings']['updateinterval'])
    # print(type(config['Settings'].getint('updateinterval')))
    # print(config['Settings']['smoothing'])
    # print(type(config['Settings'].getboolean('smoothing')))

    StripPrefix = config['Envoy'].getint('num_chars_strip')
    Scream.dbg('MainLoop','StripPrefix {}'.format(StripPrefix))

    PostInter = config['Settings'].getint('UpdateInterval')
    Scream.dbg('MainLoop','PostInter {}'.format(PostInter))

    # Setup the object to post to emoncms
    poster = WriteToEmoncmsHTTP.EMONPostHTTP(CONFIG_FILE)
    Scream.dbg('MainLoop','poster ready')

    TimeLast = time.time()
    Scream.dbg('MainLoop','TimeLast {}'.format(TimeLast))

    # Loop over stream
    for LineIn in ReceiveEnphaseStream.DataStream(config['Envoy']['ipadd'],
                                                    config['Envoy']['path'],
                                                    config['Envoy']['userid'],
                                                    config['Envoy']['userpass']):
        #print(LineIn.decode("utf-8")[6:])
        #print('\n')
        Scream.dbg('MainLoop','LineIn received')
        # The output has initial characters that need to be striped. Thus StripPrefix
        LineDict = json.loads(LineIn.decode("utf-8")[StripPrefix:])
        Scream.dbg('MainLoop','LineDict decoded')
        #print(LineDict)
        #print('\n')
        #print(LineDict["production"]["ph-a"]["p"])
        #print(type(LineDict["production"]["ph-a"]["p"]))
        #print('\n')
        if (time.time() - TimeLast) > PostInter:
            Scream.dbg('MainLoop','time good - posting')
            poster.PostToEMON(LineDict)
            TimeLast = time.time()
            
            

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
