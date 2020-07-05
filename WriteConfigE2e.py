import configparser
config = configparser.ConfigParser()


EnvoyDict = {'IPadd':'192.168.0.0100',
                'path':'/stream/meter/',
                'userID':'installer',
                'userPass':'<Installer Password>',
                'Num_Chars_Strip':6}

EmoncmsDict = {'IPadd':'127.0.0.1',
                'API_key_readwrite':'<EmonCMS Read / Write API Key>',
                'Node_Name':'EphaseData'}
                
DataDict = {'production_p':True,
            'net-consumption_p':True,
            'net-consumption_v':True,
            'total-consumption_p':False,
            'p_name':'Power',
            'v_name':'Voltage',
            'ph-a':True, 
            'ph-b':True, 
            'ph-c':False,
            'ph-a-name':'K', 
            'ph-b-name':'L'}
            

SettingsDict = {'UpdateInterval':5,
                'Smoothing':False}
                
				

# CRITICAL
# ERROR
# WARNING
# INFO
# DEBUG
# NOTSET

LogDict = {'Log_Level':'INFO',
			'Log_File':'',
			'Log_To_systemd_journal':True}
                
config['Envoy'] = EnvoyDict
config['Emoncms']   = EmoncmsDict
config['Settings']  = SettingsDict

config['Data'] = DataDict

config['Logging'] = LogDict




with open('Enphase2Emon.cfg', 'w') as configfile:
    config.write(configfile)
