#!/usr/bin/env python3

# This is an example of a daemon call. Based on 
#https://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

# Put the .pid file some place nice
 
import sys

from GenericDaemon import Daemon
import Enphase2Emon

DAEMON_PID_LOCATION = '/tmp/daemon-Enphase2Emon.pid'

class E2EDaemon(Daemon):
    def run(self):
        Enphase2Emon.MainLoop()
 
if __name__ == "__main__":
    TheDaemon = E2EDaemon(DAEMON_PID_LOCATION)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            TheDaemon.start()
        elif 'stop' == sys.argv[1]:
            TheDaemon.stop()
        elif 'restart' == sys.argv[1]:
            TheDaemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
