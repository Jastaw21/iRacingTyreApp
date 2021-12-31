import configparser


class AppConfig:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.config_dict = self.config._sections






