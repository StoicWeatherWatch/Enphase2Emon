Enphase2Emon
Get Enphase Envoy data and transfer to EmonCMS. Mostly Python

This is a Python 3 program intended to run under systemd as a daemon. It will access the stream from an Envoy S and transfer the data to EmonCMS. The system overhead is minimal. 

Requires: The Envoy S installer password
          Python 3 requests module 
                    - https://pypi.org/project/requests/
                    - https://requests.readthedocs.io/en/master/

Works on Raspberry Pi
