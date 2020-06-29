"""
Enphase2emon will receive the /stream/meter chunked http stream from an 
Enphase Envoy s and transfer the data to emoncms running locally.


ReceiveEnphaseStream handles getting the stream from the Envoy s.

"""

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

# python3 -m pip install requests
import requests
#import json

# TODO user try except
def DataStream(IPadd,AddPath,UserID,Password):
    EnphaseStream = requests.get('http://' + IPadd + AddPath, 
                                    stream=True, 
                                    auth=requests.auth.HTTPDigestAuth(UserID, Password))

    for StreamLine in EnphaseStream.iter_lines():
        if StreamLine:
            #print('\n')
            #print(b'{' + StreamLine)
            #print('\n')
            yield StreamLine