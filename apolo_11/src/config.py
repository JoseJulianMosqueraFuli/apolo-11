from pathlib import Path

import yaml


class ConfigManager:
    @staticmethod
    def read_yaml_config(config_path: str | None = None) -> dict:
        if config_path is None:
            config_path = str(Path(__file__).parent.parent / 'config/config.yaml')

        with open(config_path, "r") as config_file:
            config_data = yaml.safe_load(config_file)
            if config_data is None:
                raise ValueError(f"Configuration file is empty: {config_path}")
            return config_data
