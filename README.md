Enphase2Emon

Get Enphase Envoy data and transfer to EmonCMS.

This is a Python 3 program intended to run under systemd as a daemon. Raspberry Pi and probably many other linux flavors will run it. It will access the HTTP stream from an Envoy S and transfer the data to EmonCMS. The system overhead is minimal. Accessible data include instantaneous power, current, voltage, frequency, apparent/reactive power, and power factor ratio. Config file allows the user to select which variables and which phases to output. 


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

Uses the following standard (preinstalled) modules: sys, json, configparser, time, signal, sys, traceback, logging


Installation

Test if your envoy will work with this by pointing a web browser to 

          http://*IP Address of Envoy*/stream/meter/

Enter user installer and the installer password. You should get a stream of data that continually updates. If not, this program may not work. The installer password is NOT the last few digits of your serial number. 

Download the files to your preferred install directory

          git clone https://github.com/StoicWeatherWatch/Enphase2Emon.git

Edit Enphase2Emon.cfg. Set the IP address of the Envoy S, the install password, the API key for EmonCMS and any other settings you wish to change. If you are running EmonCMS on a Raspberry Pi with local logging and running this program on the same Raspberry Pi that keep the IP address under Emoncms at 127.0.0.1. If EmonCMS runs on some other computer from the one running this program, enter its IP address in place of 127.0.0.1.

If you keep the program directory at /home/pi/Enphase2Emon/ then no further changes need be made. Otherwise edit E2E.service and the CONFIG_FILE variable in Enphase2Emon.py to reflect the different install location.

Make certain that /tmp/ is mounted and writable. If not change DAEMON_PID_LOCATION in E2EDaemon.py and PIDFile= in E2E.service to some other location that is writable.

Make E2EDaemon.py executable. For example 

          chmod 770 E2EDaemon.py

Move E2E.service into systemd/system/. On Raspberry Pi

          sudo cp E2E.service /etc/systemd/system/

Reload the daemon list

          sudo systemctl daemon-reload

Start and enable to automatically run on restart

          sudo systemctl start E2E.service
          sudo systemctl enable E2E.service

Run

          sudo systemctl status E2E.service

The status should show some information notices form GenericDaemon and Enphase2Emon.

The EmonCMS web viewer should show new Enphase data under Inputs. It should be updated every few seconds.

