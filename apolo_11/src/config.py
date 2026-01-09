from typing import Dict

import yaml


class ConfigManager:
    @staticmethod
    def read_yaml_config(config_path: str = 'apolo_11/config/config.yaml') -> Dict:
        """
        Read YAML config from file

        Args:
            config_path (str): path to YAML configuration file

        Returns:
            dict: dictionary representing YAML configuration

        Raises:
            ValueError: if the configuration file is empty
            FileNotFoundError: if the configuration file does not exist
        """
        with open(config_path, "r") as config_file:
            config_data = yaml.safe_load(config_file)
            if config_data is None:
                raise ValueError(f"Configuration file is empty: {config_path}")
            return config_data
