#!/usr/bin/env python3

"""
This is a Python 3 daemon for Enphase2Emon which gets data from an Envoy S and
transfers it to EmonCMS. 

usage:
E2EDaemon.py start|stop|restart


"""
 
import sys

from GenericDaemon import Daemon
import Enphase2Emon

# This should match the PIDFile set in E2E.Service. Change both if you change one.
DAEMON_PID_LOCATION = '/tmp/daemon-Enphase2Emon.pid'

class E2EDaemon(Daemon):
    def run(self):
        self.LG.info('E2EDaemon run()')
        Enphase2Emon.MainLoop()
        self.LG.warning('E2EDaemon run() ending - should never get here')
 
 # This works for running directly. However a service does not call with 2 arg - unless you put them in the .service file
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
        
        # Enphase2Emon MainLoop() runs an infinite loop. It receives and handles 
        #  SIGTERM and SIGINT and exits normally on those signals. 
        #  It should never actually get to this line.
        sys.exit(30)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
        
