from .config import ConfigManager

config_path = 'apolo_11/config/config.yaml'
config = ConfigManager.read_yaml_config(config_path)

class Mission:
    """
    A class representing a mission

    Attributes:
        _name (list): list of mission names
        _codes(dict): dictionary (configfile) mapping mission names to their codes 
    """
    def __init__(self):
        """
        Initialize a Mission object
        Reads mission names and codes from the configuration file
        """
        self._name = config['missions']['names']
        self._codes = config['missions']['codes']
        
    @property
    def codes(self):
        """
        Get the mission codes
        Returns:
        dictionary mapping mission name to code
        """
        return self._codes

    @property
    def name(self):
        """
        Get list of mission name

        Returns:
        list of mission names
        """
        return self._name


class Device:
    """
    A class representing a device

    Attributes:
        _type (list): list of device types
        _status (list): list of device statuses
    """
    def __init__(self):   
        self._type = config['devices']['types']
        self._status = config['devices']['status']

    @property
    def type(self):
        """
        Get list of devise type
        """
        return self._type

    @property
    def status(self):
        """
        Get list of devise status
        """
        
        return self._status
