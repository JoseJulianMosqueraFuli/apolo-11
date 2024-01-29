from typing import List, Dict
from .config import ConfigManager


config: dict = ConfigManager.read_yaml_config()


class Configurable:
    def __init__(self, config_key):
        self._config_key = config_key
        self._load_config()

    def _load_config(self):
        self._config_data = config[self._config_key]


class Mission(Configurable):
    """
    A class representing a mission

    Attributes:
        _name (list): list of mission names
        _codes (dict): dictionary (config file) mapping mission names to their codes
    """
    def __init__(self):
        """
        Initialize a Mission object
        Reads mission names and codes from the configuration file
        """
        super().__init__('missions')

    @property
    def codes(self) -> Dict[str, str]:
        """
        Get the mission codes
        Returns:
        dictionary mapping mission name to code
        """
        return self._config_data['codes']

    @property
    def name(self) -> List[str]:
        """
        Get list of mission name

        Returns:
        list of mission names
        """
        return self._config_data['names']


class Device(Configurable):
    """
    A class representing a device

    Attributes:
        _type (list): list of device types
        _status (list): list of device statuses
    """
    def __init__(self):
        super().__init__('devices')

    @property
    def type(self) -> List[str]:
        """
        Get list of device type
        """
        return self._config_data['types']

    @property
    def status(self) -> List[str]:
        """
        Get list of device status
        """
        return self._config_data['status']
