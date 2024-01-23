import os
import random
from datetime import datetime
from typing import Union

from .config import ConfigManager
from .classes import Mission, Device

config_path: str = 'apolo_11/config/config.yaml'
config: dict = ConfigManager.read_yaml_config(config_path)

class Generator:
    def __init__(self):
        self.mission_instance: Mission = Mission()
        self.device_instance: Device = Device()
        self.generate_files_call_count: int = 0

    def generate_principal_folders(self, base_path='./apolo_11/results') -> None:
        folders: list = ['devices', 'backups', 'reports']
        for folder in folders:
            folder_path = os.path.join(base_path, folder)
            os.makedirs(folder_path, exist_ok=True)

    def generate_filename(self, mission_name, file_number)->str:
        mission_code: str = config['missions']['codes'].get(mission_name, 'UNKN')
        return f"APL{mission_code}-0000{file_number}.log"

    def generate_contentfile(self)-> str:
        mission_name: str = random.choice(self.mission_instance.name)
        device_type = random.choice(self.device_instance.type)
        device_status = random.choice(self.device_instance.status)
        date_format = config['date_format']
        current_date = datetime.now().strftime(date_format)

        if mission_name in config['missions']['codes']:
            hash_value = self.generate_hash(current_date, mission_name, device_type, device_status)
        else:
            hash_value = None

        # Optional consider posibility to content in dictionary
        content = f"Date: {current_date}, Mission: {mission_name}, " \
                  f"Device Type: {device_type}, Device Status: {device_status}, " \
                  f"Hash: {hash_value}"

        return content

    def generate_files(self, num_files_min: int, num_files_max: int):
        self.generate_files_call_count += 1
        times_stamp: str = datetime.now().strftime('%Y%m%d%H%M%S')
        output_directory: str = self.create_output_directory(times_stamp, self.generate_files_call_count)

        random_number: int = random.randint(num_files_min, num_files_max)

        for file_number in range(1, random_number + 1):
            filename: str = self.generate_filename(self.generate_contentfile().split(',')[1].split(':')[1].strip(), file_number)
            file_path: str = os.path.join(output_directory, filename)
            file_content: str = self.generate_contentfile()

            with open(file_path, 'w') as file:
                file.write(file_content)

    def create_output_directory(self, times_stamp: str, generate_files_call_count: int) -> str:
        current_directory: str = os.path.dirname(os.path.abspath(__file__))
        output_directory: str = os.path.join(current_directory, f"./../results/devices/cycle-{generate_files_call_count}-{times_stamp}")

        os.makedirs(output_directory, exist_ok=True)
        return output_directory

    def generate_hash(self, *args: Union[str, int]) -> int:
        data: str = ''.join(map(str, args))
        return hash(data)
