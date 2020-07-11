"""
Generic linux daemon base class for python 3.1 +

From original Author (in reference to the file on which this file is based):
    "This is really basic stuff and not very original. It's Public Domain, so do with it as you please."
    
This has been altered from the original form.
https://web.archive.org/web/20160305151936/http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
https://web.archive.org/web/20160320091458/http://www.jejik.com/files/examples/daemon3x.py

https://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
http://www.jejik.com/files/examples/daemon3x.py

The .pid file will hold the process ID. Put it some place nice.

To use:
    Subclass and override run() with the code you want to run. Instantiating takes
    a full path to a PID file. This file will be created to hold the process ID.

Logging is designed for a systemd journal (Raspberry Pi etc). This requires systemd-python.
Change the logging handler (in __init__) for other options. Or set KEEP_LOG = False

The process checks assume that /proc/ is mounted. 
https://man7.org/linux/man-pages/man5/proc.5.html
If this is not the case look for this command:
os.path.exists('/proc/' + str(pid))
and change it to something that will work on your system.

"""
__version__ = "0.1.0"
__author__ = "SWW"

#https://web.archive.org/web/20160305151936/http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
#https://web.archive.org/web/20160320091458/http://www.jejik.com/files/examples/daemon3x.py

import sys
import os
import time
import atexit
import signal

import logging

# Requires pip3 install systemd-python
# To remove this dependency, remove the systemd.journal import line below
#  and lines referencing systemdJournalHandler or SJHandler below in init.
#  Ideally replace it with some other logging handler. 
#  However, for quick and dirty switching off of logging,
#  add in place of the removed lines in init: self.LG.addHandler(logging.NullHandler())
from systemd.journal import JournalHandler as systemdJournalHandler


# Number of seconds to try to kill the daemon nicely on stop
TIME_OUT = 10

# Logs to output - Set to: DEBUG INFO WARNING ERROR CRITICAL
LOG_LEVEL = logging.INFO
KEEP_LOG = True


class Daemon:
    """A generic daemon class.

    Usage: subclass the daemon class and override the run() method.
    
    
    
    """

    def __init__(self, pidfile): 
        # Setup logging
        if KEEP_LOG:
            self.LG = logging.getLogger('GenericDaemon')
            #Optional datefmt='%y-%m-%d %H:%M:%S'
            LGformatter = logging.Formatter('%(asctime)s - %(name)s:%(funcName)s %(lineno)d - %(levelname)s: %(message)s')
            #https://docs.python.org/3.8/library/logging.html#logrecord-attributes
        
            # Setup for a systemd journal. Change the log handler for other logging.
            SJHandler = systemdJournalHandler(level=LOG_LEVEL)
            SJHandler.setFormatter(LGformatter)
            self.LG.addHandler(SJHandler)
            
            # This line is necessary because we must also set the minimum for the logger overall. Else it defaults to something high.
            self.LG.setLevel(LOG_LEVEL)
            self.LG.info('in progress')
        else:
            self.LG = logging.getLogger('GenericDaemon')
            self.LG.addHandler(logging.NullHandler())
        
        
        self.pidfile = pidfile
        self.TimeOut = TIME_OUT
        self.LG.info('Done')

    
    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism.
        do the UNIX double-fork magic, see Stevens' "Advanced
                Programming in the UNIX Environment" for details (ISBN 0201563177)
                http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
                
        """
        self.LG.info('daemonizing')

        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                self.LG.debug(' first fork pid > 0')
                sys.exit(0) 
        except OSError as err: 
            sys.stderr.write('fork #1 failed: {0}\n'.format(err))
            self.LG.warning('fork #1 failed: {0}\n'.format(err))
            sys.exit(1)
    
        # decouple from parent environment
        os.chdir('/') 
        os.setsid() 
        os.umask(0) 
    
        # do second fork
        self.LG.debug('second fork')
        try: 
            pid = os.fork() 
            if pid > 0:
                self.LG.debug('second fork pid > 0')

                # exit from second parent
                sys.exit(0) 
        except OSError as err: 
            sys.stderr.write('fork #2 failed: {0}\n'.format(err))
            self.LG.warning('fork #2 failed: {0}'.format(err))
            sys.exit(1) 
    
        # redirect standard file descriptors to disappear into the aether.
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')

        # I think this points standard out etc to null but I am not certain.
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
    
        # Set to remove the pid file at exit
        self.LG.debug('register delpid')
        atexit.register(self.delpid)

        # write pidfile
        pid = str(os.getpid())
        self.LG.debug('pid {}'.format(pid))
        # w+ read and write for some reason. Overwrites if exists. Odd since all we do is write.
        with open(self.pidfile,'w+') as f:
            f.write(pid + '\n')
            
        self.LG.debug('pid file written')
    
    def delpid(self):
        self.LG.debug('Removing PID File')
        os.remove(self.pidfile)

    def start(self):
        """Start the daemon"""
        self.LG.info('Starting')

        # Check for a pidfile to see if the daemon already runs
        if os.path.isfile(self.pidfile):
            self.LG.debug('open pidfile {}'.format(self.pidfile))
            with open(self.pidfile,'r') as pf:
                pid = int(pf.read().strip())
        else:
            pid = None
            self.LG.debug('(Not an error) No path to {}'.format(self.pidfile))
        
    
        if pid:
            message = "pidfile {0} already exist. " + \
                    "Daemon already running?\n"
            self.LG.warning(message.format(self.pidfile))
            sys.stderr.write(message.format(self.pidfile))
            sys.exit(1)
        
        # Start the daemon
        self.LG.debug('Calling daemonize()')
        self.daemonize()
        self.LG.debug('Calling run()')
        self.run()
        self.LG.debug(' run() done ?!? - should never get here')

    def stop(self):
        """Stop the daemon"""
        self.LG.info('Stopping')
        
        # Get the pid from the pidfile
        if os.path.isfile(self.pidfile):
            self.LG.debug('Reading pid file {}'.format(self.pidfile))
            try:
                with open(self.pidfile,'r') as pf:
                    pid = int(pf.read().strip())
                    self.LG.debug('PID read as {}'.format(pid))
            except Exception as err:
                self.LG.error('Exception opening pidfile')
                self.LG.exception("Exception opening pidfile - Trying to survive")
                pid = None
                
        else:
            self.LG.warning('os.path.isfile did not find pid file {}'.format(self.pidfile))
            pid = None
    
        if pid is None:
            message = "pidfile {0} does not exist. " + \
                    "Daemon not running?\n"
            self.LG.warning(message.format(self.pidfile))
            sys.stderr.write(message.format(self.pidfile))
            return # not an error in a restart

        # Try killing the daemon process    

        # Kill signals https://unix.stackexchange.com/questions/317492/list-of-kill-signals
        # /proc/<PID> should exist if a process is running
        if os.path.exists('/proc/' + str(pid)):
            try:
                TimeStart = time.time()
                
                # While time elapsed < time out AND path exists to the process 
                #  (The path should only exist if it is running)
                while ((time.time() - TimeStart) < self.TimeOut) and (os.path.exists('/proc/' + str(pid))):
                    self.LG.debug('Asking nicely')
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(0.1)
                    
                # If killing nicely fails the process will still be running and in /proc/
                if os.path.exists('/proc/' + str(pid)):
                    self.LG.debug('No longer asking nicely')
                    os.kill(pid, signal.SIGKILL)
            
            except OSError as err:
                e = str(err.args)
                if e.find("No such process") > 0:
                    self.LG.warning('OSError - No such process ')
                    self.LG.exception('OSError')
                    if os.path.exists(self.pidfile):
                        self.LG.debug('Removing leftover PID file')
                        os.remove(self.pidfile)
                else:
                    self.LG.error('OSError other than no such process \nError: {}'.format(str(err.args)))
                    self.LG.exception('OSError')
                    sys.exit(1)
        else:
            self.LG.warning('os.path.exists found no process {}'.format(str(pid)))
            if os.path.exists(self.pidfile):
                self.LG.debug('Removing leftover PID file')
                os.remove(self.pidfile)
            

    def restart(self):
        """Restart the daemon"""
        self.LG.debug('Restarting')
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon.
        
        It will be called after the process has been daemonized by 
        start() or restart().
        """
        # If you call super().run() You will see:
        self.LG.info('Run starting')
