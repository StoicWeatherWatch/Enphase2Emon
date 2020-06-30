"""
Enphase2Emon will receive the /stream/meter chunked http stream from an 
Enphase Envoy s and transfer the data to EmonCMS running locally.


Enphase2Emon.py is the core program.

Also uses
ReceiveEnphaseStream.py
WriteToEmoncmsHTTP.py
"""

__version__ = "0.0.1"
__author__ = "SWW"

CONFIG_FILE = 'Enphase2emon.cfg'

# Local Files
import ReceiveEnphaseStream
import WriteToEmoncmsHTTP

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

# Read config file
# TODO user try except
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# print(config['Envoy']['ipadd'])
# print(type(config['Envoy']['ipadd']))
# print(config['Settings']['updateinterval'])
# print(type(config['Settings'].getint('updateinterval')))
# print(config['Settings']['smoothing'])
# print(type(config['Settings'].getboolean('smoothing')))

StripPrefix = config['Envoy'].getint('num_chars_strip')

PostInter = config['Settings'].getint('UpdateInterval')

# Setup the object to post to emoncms
poster = WriteToEmoncmsHTTP.EMONPostHTTP(CONFIG_FILE)

TimeLast = time.time()

# Loop over stream
for LineIn in ReceiveEnphaseStream.DataStream(config['Envoy']['ipadd'],
												config['Envoy']['path'],
												config['Envoy']['userid'],
												config['Envoy']['userpass']):
    #print(LineIn.decode("utf-8")[6:])
    #print('\n')
    
    # The output has initial characters that need to be striped. Thus StripPrefix
    LineDict = json.loads(LineIn.decode("utf-8")[StripPrefix:])
    #print(LineDict)
    #print('\n')
    #print(LineDict["production"]["ph-a"]["p"])
    #print(type(LineDict["production"]["ph-a"]["p"]))
    #print('\n')
    if (time.time() - TimeLast) > PostInter:
    	poster.PostToEMON(LineDict)
    	TimeLast = time.time()
    
    
    

