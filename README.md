Enphase2Emon

Get Enphase Envoy data and transfer to EmonCMS. Mostly Python

This is a Python 3 program intended to run under systemd as a daemon. It will access the HTTP stream from an Envoy S and transfer the data to EmonCMS. The system overhead is minimal. Accessible data include instantaneous power, current, voltage, frequency, apparent/reactive power, and power factor ratio. Config file allows the user to select which variables and which phases to output. 

Requires: 

The Envoy S installer password

Python 3 requests 

          https://pypi.org/project/requests/
          
          https://requests.readthedocs.io/en/master/
          
          pip3 install requests

Python 3 systemd-python

          https://pypi.org/project/systemd-python/          
          
          https://github.com/systemd/python-systemd
          
          pip3 install systemd-python
          
          Oddly imported as 
          import systemd
          
          May be able to substitute https://pypi.org/project/systemd/
          Look for the line below in code and make appropriate adjustments
          from systemd.journal import JournalHandler as systemdJournalHandler

Uses the following standard modules: sys, json, configparser, time, signal, sys, traceback, logging

Works on Raspberry Pi. Should be portable to other linux systems. 
