import configparser
config = configparser.ConfigParser()
config.read('config.ini')
#GPIO = config['GPIO']
print(config['GPIO']['TopSensor'])
