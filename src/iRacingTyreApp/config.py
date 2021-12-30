import configparser

config = configparser.ConfigParser()

opts = config.read('config.ini')

name = config['common']['jack']
print(name)