import os
import yaml

class ConfigManager:
    @staticmethod
    def read_yaml_config(config_path):
        with open(config_path, "r") as config_file:
            return yaml.safe_load(config_file)
    
