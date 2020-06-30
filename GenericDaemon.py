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
#__version__ = "0.0.2"

#https://web.archive.org/web/20160305151936/http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
#https://web.archive.org/web/20160320091458/http://www.jejik.com/files/examples/daemon3x.py

import sys
import os
import time
import atexit
import signal

from Screamer import Screamer

class Daemon:
    """A generic daemon class.

    Usage: subclass the daemon class and override the run() method.
    
    
    
    """

    def __init__(self, pidfile): 
        self.pidfile = pidfile
        self.Scream = Screamer.LocalOnly('Generic Daemon')
        self.Scream.msg('__init__','Done')
    
    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism.
        do the UNIX double-fork magic, see Stevens' "Advanced
                Programming in the UNIX Environment" for details (ISBN 0201563177)
                http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
                
        """
        self.Scream.msg('daemonize','Start')

        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                self.Scream.dbg('daemonize','pid > 0')
                sys.exit(0) 
        except OSError as err: 
            sys.stderr.write('fork #1 failed: {0}\n'.format(err))
            self.Scream.Alert('daemonize','fork #1 failed: {0}\n'.format(err))
            sys.exit(1)
    
        # decouple from parent environment
        os.chdir('/') 
        os.setsid() 
        os.umask(0) 
    
        # do second fork
        self.Scream.dbg('daemonize','second fork')
        try: 
            pid = os.fork() 
            if pid > 0:
                self.Scream.dbg('daemonize','pid > 0')

                # exit from second parent
                sys.exit(0) 
        except OSError as err: 
            sys.stderr.write('fork #2 failed: {0}\n'.format(err))
            self.Scream.Alert('daemonize','fork #2 failed: {0}'.format(err))
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
        self.Scream.dbg('daemonize','register delpid')
        atexit.register(self.delpid)

        # write pidfile
        pid = str(os.getpid())
        self.Scream.dbg('daemonize','pid {}'.format(pid))
        # w+ read and write for some reason. Overwrites if exists. Odd since all we do is write.
        with open(self.pidfile,'w+') as f:
    
            f.write(pid + '\n')
            
        self.Scream.dbg('daemonize','pid file written')
    
    def delpid(self):
        self.Scream.dbg('delpid','Running')
        os.remove(self.pidfile)

    def start(self):
        """Start the daemon"""
        self.Scream.msg('start','Starting')

        # Check for a pidfile to see if the daemon already runs
        # TODO Do this without hacking try except. (This is soposed to except)
        try:
            self.Scream.dbg('start','open pidfile {}'.format(self.pidfile))
            with open(self.pidfile,'r') as pf:

                pid = int(pf.read().strip())
        except IOError:
            pid = None
            self.Scream.dbg('start','IOError')
    
        if pid:
            message = "pidfile {0} already exist. " + \
                    "Daemon already running?\n"
            self.Scream.Alert('start',message.format(self.pidfile))
            sys.stderr.write(message.format(self.pidfile))
            sys.exit(1)
        
        # Start the daemon
        self.Scream.dbg('start','Calling daemonize()')
        self.daemonize()
        self.Scream.dbg('start','Calling run()')
        self.run()
        self.Scream.dbg('start',' run() done ?!? - should not get here')

    def stop(self):
        """Stop the daemon"""
        self.Scream.dbg('stop','Stopping')
        # Get the pid from the pidfile
        try:
            self.Scream.dbg('stop','Reading pid file {}'.format(self.pidfile))
            with open(self.pidfile,'r') as pf:
                pid = int(pf.read().strip())
                self.Scream.dbg('stop','PID read as {}'.format(pid))
        except IOError:
            self.Scream.Alert('stop','IOError')
            pid = None
    
        if not pid:
            message = "pidfile {0} does not exist. " + \
                    "Daemon not running?\n"
            self.Scream.Alert('stop',message.format(self.pidfile))
            sys.stderr.write(message.format(self.pidfile))
            return # not an error in a restart

        # Try killing the daemon process    
        # TODO re write with a break otu from the infinite loop
        # TODO rewrite check for process first.
        # Kill signals https://unix.stackexchange.com/questions/317492/list-of-kill-signals
        try:
            while 1:
                self.Scream.dbg('stop','In the infinite loop')
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
                # os.kill(pid, signal.SIGKILL)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                self.Scream.Alert('stop','OSError other than no such process \nError: {}'.format(str(err.args)))
                print (str(err.args))
                sys.exit(1)

    def restart(self):
        """Restart the daemon"""
        self.Scream.dbg('restart','restarting')
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon.
        
        It will be called after the process has been daemonized by 
        start() or restart().
        """
