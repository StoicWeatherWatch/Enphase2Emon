"""
Generic linux daemon base class for python 3.x.

From original Author:
    This is really basic stuff and not very original. It's Public Domain, so do with it as you please.
    
This may be altered from the original form.
https://web.archive.org/web/20160305151936/http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
https://web.archive.org/web/20160320091458/http://www.jejik.com/files/examples/daemon3x.py

https://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
http://www.jejik.com/files/examples/daemon3x.py

The .pid file will hold the process ID. Put it some place nice.

"""

#https://web.archive.org/web/20160305151936/http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
#https://web.archive.org/web/20160320091458/http://www.jejik.com/files/examples/daemon3x.py

import sys
import os
import time
import atexit
import signal

class Daemon:
    """A generic daemon class.

    Usage: subclass the daemon class and override the run() method.
    
    
    
    """

    def __init__(self, pidfile): 
        self.pidfile = pidfile
    
    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism.
        do the UNIX double-fork magic, see Stevens' "Advanced
                Programming in the UNIX Environment" for details (ISBN 0201563177)
                http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
                
        """

        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError as err: 
            sys.stderr.write('fork #1 failed: {0}\n'.format(err))
            sys.exit(1)
    
        # decouple from parent environment
        os.chdir('/') 
        os.setsid() 
        os.umask(0) 
    
        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:

                # exit from second parent
                sys.exit(0) 
        except OSError as err: 
            sys.stderr.write('fork #2 failed: {0}\n'.format(err))
            sys.exit(1) 
    
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
    
        # Set to remove the pid file at exit
        atexit.register(self.delpid)

        # write pidfile
        pid = str(os.getpid())
        # w+ read and write for some reason. Overwrites if exists. Odd since all we do is write.
        with open(self.pidfile,'w+') as f:
            f.write(pid + '\n')
    
    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """Start the daemon"""

        # Check for a pidfile to see if the daemon already runs
        try:
            with open(self.pidfile,'r') as pf:

                pid = int(pf.read().strip())
        except IOError:
            pid = None
    
        if pid:
            message = "pidfile {0} already exist. " + \
                    "Daemon already running?\n"
            sys.stderr.write(message.format(self.pidfile))
            sys.exit(1)
        
        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """Stop the daemon"""

        # Get the pid from the pidfile
        try:
            with open(self.pidfile,'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None
    
        if not pid:
            message = "pidfile {0} does not exist. " + \
                    "Daemon not running?\n"
            sys.stderr.write(message.format(self.pidfile))
            return # not an error in a restart

        # Try killing the daemon process    
        # TODO re write with a break otu from the infinite loop
        # TODO rewrite check for process first.
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print (str(err.args))
                sys.exit(1)

    def restart(self):
        """Restart the daemon"""
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon.
        
        It will be called after the process has been daemonized by 
        start() or restart().
        """
