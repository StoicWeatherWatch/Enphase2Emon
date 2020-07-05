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
import sys
#import json

# If we go longer than this time without any activity, it will except Timeout
STREAM_TIME_OUT = 5

class E2EReceiveError_Fatal(Exception):
    """
    Any error that cannot be recovered. Will cause the main program to quit. 
    Hopefully the daemon will restart.
    """
    def __init__(self, location, message, cause):
        """
        location : String where in the code it comes from
        message : String Description
        cause : a caught exception that caused the problem. Or None.
        """
        self.location = location
        self.message = message
        self.cause = cause



# TODO user try except
def DataStream(IPadd,AddPath,UserID,Password):
    
    try:
        EnphaseStream = requests.get('http://' + IPadd + AddPath, 
                                        stream=True, 
                                        auth=requests.auth.HTTPDigestAuth(UserID, Password),
                                        timeout=STREAM_TIME_OUT)
        
        
        # This will raise HTTPError if the HTTP status code is in the 400s or 500s
        EnphaseStream.raise_for_status() 
    except requests.exceptions.HTTPError as err:
        if (EnphaseStream.status_code) and isinstance(EnphaseStream.status_code, int):
            StatusCode = EnphaseStream.status_code
        else:
            StatusCode = None
        tb = sys.exc_info()[2]
        raise E2EReceiveError_Fatal('ReceiveEnphaseStream DataStream(*) - requests.get(*)', 'HTTP status code {}'.format(StatusCode), err).with_traceback(tb)
    except requests.exceptions.Timeout  as err:
        tb = sys.exc_info()[2]
        raise E2EReceiveError_Fatal('ReceiveEnphaseStream DataStream(*) - requests.get(*)', 'Request timed out', err).with_traceback(tb)
    except requests.exceptions.RequestException  as err:
        tb = sys.exc_info()[2]
        raise E2EReceiveError_Fatal('ReceiveEnphaseStream DataStream(*) - requests.get(*)', 'Unknown HTTP error', err).with_traceback(tb)
        
    try:
        for StreamLine in EnphaseStream.iter_lines():
            # This will raise HTTPError if the HTTP status code is in the 400s or 500s. No idea if it works in an iterater like this. 
            EnphaseStream.raise_for_status() 
            if StreamLine:
                yield StreamLine
                      
    except requests.exceptions.HTTPError as err:
        if (EnphaseStream.status_code) and isinstance(EnphaseStream.status_code, int):
            StatusCode = EnphaseStream.status_code
        else:
            StatusCode = None
        tb = sys.exc_info()[2]
        raise E2EReceiveError_Fatal('ReceiveEnphaseStream DataStream(*) - requests.get(*) loop', 'HTTP status code {}'.format(StatusCode), err).with_traceback(tb)
    except requests.exceptions.Timeout  as err:
        tb = sys.exc_info()[2]
        raise E2EReceiveError_Fatal('ReceiveEnphaseStream DataStream(*) - requests.get(*) loop', 'Request timed out', err).with_traceback(tb)
    except requests.exceptions.RequestException  as err:
        tb = sys.exc_info()[2]
        raise E2EReceiveError_Fatal('ReceiveEnphaseStream DataStream(*) - requests.get(*) loop', 'Unknown HTTP error', err).with_traceback(tb)
        

# tb = sys.exc_info()[2]
#    raise OtherException(...).with_traceback(tb
# Exceptions
# requests.exceptions.Timeout
# requests.exceptions.ConnectionError
# requests.exceptions.HTTPError
# requests.exceptions.RequestException

# Raise and exit abnormal - it should restart

# EnphaseStream.raise_for_status()
#EnphaseStream.status_code

# https://requests.readthedocs.io/en/master/_modules/requests/exceptions/

'''
Exceptions
exception requests.RequestException(*args, **kwargs)[source]
There was an ambiguous exception that occurred while handling your request.

exception requests.ConnectionError(*args, **kwargs)[source]
A Connection error occurred.

exception requests.HTTPError(*args, **kwargs)[source]
An HTTP error occurred.

exception requests.URLRequired(*args, **kwargs)[source]
A valid URL is required to make a request.

exception requests.TooManyRedirects(*args, **kwargs)[source]
Too many redirects.

exception requests.ConnectTimeout(*args, **kwargs)[source]¶
The request timed out while trying to connect to the remote server.

Requests that produced this error are safe to retry.

exception requests.ReadTimeout(*args, **kwargs)[source]
The server did not send any data in the allotted amount of time.

exception requests.Timeout(*args, **kwargs)[source]
The request timed out.

Catching this error will catch both ConnectTimeout and ReadTimeout errors.'''
