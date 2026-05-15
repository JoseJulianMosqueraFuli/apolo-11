from .config import ConfigManager


class Configurable:
    def __init__(self, config_key: str, config_data: dict | None = None):
        self._config_key = config_key
        if config_data is None:
            config_data = ConfigManager.read_yaml_config()
        self._config_data = config_data[self._config_key]


class Mission(Configurable):
    def __init__(self, config_data: dict | None = None):
        super().__init__('missions', config_data=config_data)

    @property
    def codes(self) -> dict[str, str]:
        return self._config_data['codes']

    @property
    def name(self) -> list[str]:
        return self._config_data['names']


class Device(Configurable):
    def __init__(self, config_data: dict | None = None):
        super().__init__('devices', config_data=config_data)

    @property
    def type(self) -> list[str]:
        return self._config_data['types']

    @property
    def status(self) -> list[str]:
        return self._config_data['status']
