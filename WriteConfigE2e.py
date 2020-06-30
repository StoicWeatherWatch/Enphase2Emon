import configparser
config = configparser.ConfigParser()


EnvoyDict = {'IPadd':'192.168.0100',
                'path':'/stream/meter/',
                'userID':'installer',
                'userPass':'<Installer Password>',
                'Num_Chars_Strip':6}

EmoncmsDict = {'IPadd':'127.0.0.1',
                'API_key_readwrite':'<EmonCMS Read / Write API Key>',
                'Node_Name':'EphaseData'}
                
DataDict = {'production_p':True,
            'net-consumption_P':True,
            'total-consumption_P':False,
            'p_name':'Power',
            'ph-a':True, 
            'ph-b':True, 
            'ph-c':False,
            'ph-a-name':'K', 
            'ph-b-name':'L'}
            

SettingsDict = {'UpdateInterval':5,
                'Smoothing':False}
                
config['Envoy'] = EnvoyDict
config['Emoncms']   = EmoncmsDict
config['Settings']  = SettingsDict

config['Data'] = DataDict




with open('Enphase2Emon.cfg', 'w') as configfile:
    config.write(configfile)
