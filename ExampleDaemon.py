#!/usr/bin/env python3
'''
# This is an example of a daemon subclass. Based on 
#https://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

# Put the .pid file some place nice in DAEMON_LOCATION

To use with a systemctl service, on Raspberry Pi or simular systems,
create a .service file such as below

# exampleD.service
[Unit]
Description=Example service
After=network.target
StartLimitIntervalSec=180
StartLimitBurst=6

[Service]
ExecStart=/home/pi/<DaemonDirectory>/ExampleDaemon.py start
ExecReload=/home/pi/<DaemonDirectory>/ExampleDaemon.py restart
ExecStop=/home/pi/<DaemonDirectory>/ExampleDaemon.py stop
WorkingDirectory=/home/pi/<DaemonDirectory>/
StandardOutput=inherit
StandardError=inherit

# Options on-failure on-abnormal etc
Restart=on-failure
RestartSec=10
User=pi
Type=forking

# This should match DAEMON_LOCATION below.
PIDFile=/tmp/daemon-example.pid


[Install]
WantedBy=multi-user.target

# End of exampleD.service

Put the .service file in /etc/systemd/system/ or equivalent.

Terminal commands
# Run this after any change or addition to the .service file
sudo systemctl daemon-reload


sudo systemctl start exampleD.service
sudo systemctl stop exampleD.service
# restart runs the stop command in ExecStop then the start command in ExecStart
sudo systemctl restart exampleD.service
# reload runs ExecReload.
#  Convention is to reload config files without stopping and starting. 
#  Our simple example does not follow this. Reload calls restart from GenericDaemon
sudo systemctl reload exampleD.service

# To start every time the computer starts, use enable
sudo systemctl enable exampleD.service
sudo systemctl disable exampleD.service

sudo systemctl status exampleD.service

'''
 
import sys
# time only needed for demo
import time

from GenericDaemon import Daemon

# import <Some Module I Made>

DAEMON_LOCATION = '/tmp/daemon-example.pid'
 
class MyDaemon(Daemon):
    def run(self):
        self.LG.info('MyDaemon run()')
        # Instantiate and run <Some Module I Made> below.
        while True:
            time.sleep(1)
 
if __name__ == "__main__":
    daemon = MyDaemon(DAEMON_LOCATION)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
        
