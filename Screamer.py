"""
Screamer is a class for communicating from the program to the programmer. 

It handles logging to standard unix type logs and printing to the terminal.

Instantiating Screamer involves sending it settings for how much to communicate and where.


"""

#__version__ = "0.0.1"
__author__ = "SWW"

DEFAULTS = {'Local_Log':'',
            'Log_Debug_Msg':False,
            'Print_Debug_Msg_To_Terminal':False}
            
DONOTHING = {'Local_Log':'',
                'Log_Debug_Msg':False,
                'Print_Debug_Msg_To_Terminal':False}

KITCHENSINK = {'Local_Log':'/home/pi/LocalLog.txt',
                'Log_Debug_Msg':True,
                'Print_Debug_Msg_To_Terminal':True}

FULLLOG = {'Local_Log':'/home/pi/LocalLog.txt',
            'Log_Debug_Msg':True,
            'Print_Debug_Msg_To_Terminal':False}

LOCALONLY = {'Local_Log':'/home/pi/LocalLog.txt',
            'Log_Debug_Msg':False,
            'Print_Debug_Msg_To_Terminal':False}

class Screamer:
    """
    Class to hold our settings and send communications.
    """
    
    def __init__(self, SettingsDict=None, ProgramName=''):
        if SettingsDict is None:
            SettingsDict = DEFAULTS
            
        self.ProgramName = ProgramName
            
        self.LogDebugMsg = SettingsDict['Log_Debug_Msg']
        self.PrintDebugToTerminal = SettingsDict['Print_Debug_Msg_To_Terminal']
        
        if SettingsDict['Local_Log'] != '':
            self.LocalLog = SettingsDict['Local_Log']
        else:
            self.LocalLog = None
        
    
    @classmethod
    def LogNothing(cls, ProgramName=''):
        SettingsDict = DONOTHING
        
        TheScreamer = cls(SettingsDict,ProgramName)
        return TheScreamer
        
    @classmethod
    def FullDebug(cls, ProgramName=''):
        SettingsDict = KITCHENSINK
        
        TheScreamer = cls(SettingsDict, ProgramName)
        return TheScreamer
        
    @classmethod
    def LogDebug(cls, ProgramName=''):
        SettingsDict = FULLLOG
        
        TheScreamer = cls(SettingsDict, ProgramName)
        return TheScreamer
        
    @classmethod
    def LocalOnly(cls, ProgramName=''):
        SettingsDict = LOCALONLY
        
        TheScreamer = cls(SettingsDict, ProgramName)
        return TheScreamer
        
    def PrintSettings(self):
        print(self.ProgramName)
        print(self.LogDebugMsg)
        print(self.PrintDebugToTerminal)
        print(__name__)
    
    def msg(self,Caller,LineIn):
        if self.PrintDebugToTerminal:
            print('{Program} - {SubProcess} Msg: {Msg}'.format(Program = self.ProgramName, SubProcess = Caller, Msg = LineIn))
        
        if self.LocalLog is not None:
            with open(self.LocalLog,'a') as LogFile:
                LogFile.write('{Program} - {SubProcess} Msg: {Msg}\n'.format(Program = self.ProgramName, SubProcess = Caller, Msg = LineIn))
    
    
    def dbg(self,Caller,LineIn):
        if self.PrintDebugToTerminal:
            print('{Program} - {SubProcess} DBG: {Msg}'.format(Program = self.ProgramName, SubProcess = Caller, Msg = LineIn))
        
        if self.LocalLog is not None:
            with open(self.LocalLog,'a') as LogFile:
                LogFile.write('{Program} - {SubProcess} DBG: {Msg}\n'.format(Program = self.ProgramName, SubProcess = Caller, Msg = LineIn))
    
    def Alert(self,Caller,LineIn):
        if self.PrintDebugToTerminal:
            print('{Program} - {SubProcess} Alert: {Msg}'.format(Program = self.ProgramName, SubProcess = Caller, Msg = LineIn))
        
        if self.LocalLog is not None:
            with open(self.LocalLog,'a') as LogFile:
                LogFile.write('{Program} - {SubProcess} Alert: {Msg}\n'.format(Program = self.ProgramName, SubProcess = Caller, Msg = LineIn))
    