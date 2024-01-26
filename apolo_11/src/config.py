import os
import yaml

class ConfigManager:
    @staticmethod
    def read_yaml_config(config_path):
        """
        Read YAML config from file

        Args:
            config_path (str): path to YAML configuration file

        Returns:
            dict: dictionary representing YAML configuration
        """
        with open(config_path, "r") as config_file:
            return yaml.safe_load(config_file)
    
