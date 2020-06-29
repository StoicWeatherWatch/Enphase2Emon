"""
Enphase2emon will receive the /stream/meter chunked http stream from an 
Enphase Envoy s and transfer the data to emoncms running locally.


WriteToEmoncmsHTTP handles writing data to Emoncms.

"""

import configparser
import json
import requests



#http://emonpi.local/input/post?node=mynode&fulljson={"power1":100,"power2":200,"power3":300}&apikey=fc9c9ae50942b35f8a1baa67649e301b

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
        print('EMONPostHTTP __init__')
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
        
        #print(self.Phases)
        
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
                
        #print(self.SolarProductionDataTypes)
        #print(self.MainsConsumptionDataTypes)
        #print(self.TotalConsumptionDataTypes)
        
        self.EmonNodeName = config['Emoncms']['Node_Name']
        
        self.IPadd = config['Emoncms']['ipadd']
        self.APIKey = config['Emoncms']['api_key_readwrite']

        
        
    def ProcessData(self, DataBlockDict):
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
        
        #print(DataOutDict)
        
        DataString = json.dumps(DataOutDict, separators=(',', ':'))
        print(type(DataString))
        
        return DataString # JSON string for output
    
    def SendData(self, DataString):
        # Assemble http string
        SendString = ''.join(['http://', 
                        self.IPadd,
                        '/input/post?node=',
                        self.EmonNodeName,
                        '&fulljson=',
                        DataString,
                        '&apikey=',
                        self.APIKey])
        
        print(SendString)
        
        result = requests.get(SendString)
        
        print(result)
        
        
    def PostToEMON(self, DataBlockDict):
        DataString = self.ProcessData(DataBlockDict)
        print(DataString)
        self.SendData(DataString)
            
#http://192.168.0.8/input/post?node=EphaseData&fulljson={"Solar_Power_K":411.886,"Mains_Power_K":1341.243,"Solar_Power_L":412.632,"Mains_Power_L":1400.988}&apikey=809ebd23640fbddb475af911ad91e7c0