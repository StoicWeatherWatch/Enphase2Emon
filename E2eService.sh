#!/bin/sh

# Runs Enphase2emon.py

# service --status-all

# Probably should be more like this
# https://stackoverflow.com/questions/3430330/best-way-to-make-a-shell-script-daemon

#https://www.raspberrypi.org/documentation/linux/usage/systemd.md

python3 -u /home/pi/Enphase2emon/Enphase2emon.py

#https://www.raspberrypi.org/documentation/linux/usage/systemd.md
# sudo cp E2e.service /etc/systemd/system/E2e.service

# sudo systemctl start myscript.service
# sudo systemctl enable myscript.service
#restart
#disable