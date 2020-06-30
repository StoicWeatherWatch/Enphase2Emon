#!/usr/bin/env python3

# This is an example of a daemon call. Based on 
#https://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

# Put the .pid file some place nice
 
import sys
import time
from GenericDaemon import Daemon

DAEMON_LOCATION = '/tmp/daemon-example.pid'
 
class MyDaemon(Daemon):
    def run(self):
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