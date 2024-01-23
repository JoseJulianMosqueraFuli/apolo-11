from .config import ConfigManager

config_path = 'apolo_11/config/config.yaml'
config = ConfigManager.read_yaml_config(config_path)

class Mission:
    def __init__(self):
        self._name = config['missions']['names']
        self._codes = config['missions']['codes']
        
    @property
    def codes(self):
        return self._codes
      
    @property
    def name(self):
        return self._name


class Device:
    def __init__(self):
        self._type = config['devices']['types']
        self._status = config['devices']['status']

    @property
    def type(self):
        return self._type

    @property
    def status(self):
        return self._status
