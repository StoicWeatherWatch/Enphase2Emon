"""
Enphase2emon will receive the /stream/meter chunked http stream from an 
Enphase Envoy s and transfer the data to emoncms running locally.


WriteToEmoncmsHTTP handles writing data to Emoncms.

"""

import configparser
import json
import requests
import logging
import sys

# If we go longer than this time without any response from EmonCMS, it will except Timeout
SEND_TIME_OUT = 5


class E2EPosterError_Fatal(Exception):
    """
    Any error that cannot be recovered. Will cause the main program to quit. 
    Hopefully the daemon will restart.
    """
    def __init__(self, location, message, cause):
        """
        location : String where in the code it comes from
        message : String Description
        cause : a caught exception that caused the problem. Or None.
        """
        self.location = location
        self.message = message
        self.cause = cause


class EMONPostHTTP:
    """
    EMONPostHTTP holds the constants for posting data and posts input to emoncms
    
    format
    http://emonpi.local/input/post?node=mynode&fulljson={"power1":100,"power2":200,"power3":300}&apikey=fc9c9ae50942b35f8a1baa67649e301b
    
    http://emonpi.local/input/post?
    node=mynode
    &fulljson={"power1":100,"power2":200,"power3":300}
    &apikey=fc9c9ae50942b35f8a1baa67649e301b
    
    """
    
    def __init__(self, ConfigFileName):
        # <Main Logger>.<Sub Logger> should inherit the configuration from the main
        self.LG = logging.getLogger('Enphase2Emon.EMONPostHTTP')
        self.LG.info('EMONPostHTTP __init__')
        
        config = configparser.ConfigParser()
        config.read(ConfigFileName)
        
        
        # Which phases are we interested in
        self.Phases = {}
        if config['Data'].getboolean('ph-a'):
            self.Phases.update({'ph-a':config['Data']['ph-a-name']})
        if config['Data'].getboolean('ph-b'):
            self.Phases.update({'ph-b':config['Data']['ph-b-name']})
        if config['Data'].getboolean('ph-c'):
            self.Phases.update({'ph-c':config['Data']['ph-c-name']})
        
        self.LG.debug('self.Phases {}'.format(str(self.Phases)))
        
        
        # Which variables are we passing to EmonCMS
        self.SolarProductionDataTypes = {}
        self.MainsConsumptionDataTypes = {}
        self.TotalConsumptionDataTypes = {}
        
        DataTypes = ['p','i','v']
        
        for DataType in DataTypes:
            if config['Data'].getboolean('production_' + DataType):
                self.SolarProductionDataTypes.update({DataType:config['Data'][DataType+'_name']})
            
            if config['Data'].getboolean('net-consumption_' + DataType):
                self.MainsConsumptionDataTypes.update({DataType:config['Data'][DataType+'_name']})
            
            if config['Data'].getboolean('total-consumption_' + DataType):
                self.TotalConsumptionDataTypes.update({DataType:config['Data'][DataType+'_name']})
                

        self.LG.debug('self.SolarProductionDataTypes {}'.format(str(self.SolarProductionDataTypes)))
        self.LG.debug('self.MainsConsumptionDataTypes {}'.format(str(self.MainsConsumptionDataTypes)))
        self.LG.debug('self.TotalConsumptionDataTypes {}'.format(str(self.TotalConsumptionDataTypes)))
        
        # This is the node label that appears in EmonCMS
        self.EmonNodeName = config['Emoncms']['Node_Name']
        
        self.IPadd = config['Emoncms']['ipadd']
        self.APIKey = config['Emoncms']['api_key_readwrite']

        
        
    def ProcessData(self, DataBlockDict):
        """
        Extract desired data from input dictionary and format for upload
        """
        DataOutDict = {}
        for PhaseKey, PhaseName in self.Phases.items():
            # Solar Production
            for DataType, DataName in self.SolarProductionDataTypes.items():
                DataPoint = DataBlockDict['production'][PhaseKey][DataType]
                DataName = 'Solar' + '_' + DataName + '_' + PhaseName
                DataOutDict.update({DataName:DataPoint})
            # Mains Draw
            for DataType, DataName in self.MainsConsumptionDataTypes.items():
                DataPoint = DataBlockDict['net-consumption'][PhaseKey][DataType]
                DataName = 'Mains' + '_' + DataName + '_' + PhaseName
                DataOutDict.update({DataName:DataPoint})
            # Total (Sum)
            for DataType, DataName in self.TotalConsumptionDataTypes.items():
                DataPoint = DataBlockDict['total-consumption'][PhaseKey][DataType]
                DataName = 'TotalMainsSolar' + '_' + DataName + '_' + PhaseName
                DataOutDict.update({DataName:DataPoint})
        

        self.LG.debug('DataOutDict {}'.format(str(DataOutDict)))
        
        DataString = json.dumps(DataOutDict, separators=(',', ':'))

        return DataString # JSON string for output
    
    
    def SendData(self, DataString):
        """
        Send to EmonCMS
        """
        # Assemble http string
        SendString = ''.join(['http://', 
                        self.IPadd,
                        '/input/post?node=',
                        self.EmonNodeName,
                        '&fulljson=',
                        DataString,
                        '&apikey=',
                        self.APIKey])
        
        self.LG.debug('SendString {}'.format(SendString))
        
        try:
            result = requests.get(SendString, timeout=SEND_TIME_OUT)
            
            result.raise_for_status() 
        except requests.exceptions.HTTPError as err:
            if (result.status_code) and isinstance(result.status_code, int):
                StatusCode = result.status_code
            else:
                StatusCode = None
            tb = sys.exc_info()[2]
            raise E2EPosterError_Fatal('WriteToEmoncmsHTTP SendData(*) - requests.get(*)', 'HTTP status code {}'.format(StatusCode), err).with_traceback(tb)
        except requests.exceptions.Timeout  as err:
            tb = sys.exc_info()[2]
            raise E2EPosterError_Fatal('WriteToEmoncmsHTTP SendData(*) - requests.get(*)', 'Request timed out', err).with_traceback(tb)
        except requests.exceptions.RequestException  as err:
            tb = sys.exc_info()[2]
            raise E2EPosterError_Fatal('WriteToEmoncmsHTTP SendData(*) - requests.get(*)', 'Unknown HTTP error', err).with_traceback(tb)
        

        self.LG.debug('result {}'.format(result))
        
        
    def PostToEMON(self, DataBlockDict):
        DataString = self.ProcessData(DataBlockDict)
        self.LG.debug('DataString {}'.format(DataString))
        self.SendData(DataString)
            
