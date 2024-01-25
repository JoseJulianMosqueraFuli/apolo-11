import os
import random
import uuid
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

    def generate_device_folder(self, base_path='./apolo_11/results') -> None:
        folder: str = 'devices'
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path, exist_ok=True)

    def generate_filename(self, mission_name, file_number) -> str:
        mission_code: str = config['missions']['codes'].get(mission_name, 'UNKN')
        return f"APL{mission_code}-{file_number:04d}.log"

    def generate_contentfile(self, file_number: int) -> str:
        mission_name: str = random.choice(self.mission_instance.name)
        device_type: str = random.choice(self.device_instance.type)
        device_status: str = random.choice(self.device_instance.status)
        date_format: str = config['date_format']
        current_date: str = datetime.now().strftime(date_format)

        if mission_name in config['missions']['codes']:
            hash_value: int = self.generate_hash(current_date, mission_name, device_type, device_status)
            content = f"Date: {current_date}\nMission: {mission_name}\n" \
                      f"Device Type: {device_type}\nDevice Status: {device_status}\n" \
                      f"Hash: {hash_value}"
        else:
            hash_value = 'unknown'
            device_status = 'unknown'
            device_type = 'unknown'
            unique_id = uuid.uuid4()
            content = f"Date: {current_date}\nMission: {mission_name}\n" \
                      f"Device Type: {device_type}\nDevice Status: {device_status}\n" \
                      f"Hash: {hash_value}\nID: {unique_id}"

        filename = self.generate_filename(mission_name, file_number)

        return filename, content

    def generate_files(self, num_files_min: int, num_files_max: int):
        try:
            self.load_cycle_number()
            times_stamp: str = datetime.now().strftime('%Y%m%d%H%M%S')
            output_directory: str = self.create_output_directory(times_stamp, self.generate_files_call_count)

            random_number: int = random.randint(num_files_min, num_files_max)

            for file_number in range(1, random_number + 1):
                filename, file_content = self.generate_contentfile(file_number)
                file_path: str = os.path.join(output_directory, filename)

                with open(file_path, 'w') as file:
                    file.write(file_content)

            self.save_cycle_number()

        except KeyboardInterrupt:
            print("Files generation stopped by keyboard interrupt")

    def load_cycle_number(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), 'cycle_number.txt'), 'r') as file:
                self.generate_files_call_count = int(file.read().strip())
        except FileNotFoundError:
            self.generate_files_call_count = 0
            self.save_cycle_number()

    def save_cycle_number(self):
        self.generate_files_call_count += 1

        with open(os.path.join(os.path.dirname(__file__), 'cycle_number.txt'), 'w') as file:
            file.write(str(self.generate_files_call_count))

    def create_output_directory(self, times_stamp: str, generate_files_call_count: int) -> str:
        current_directory: str = os.path.dirname(os.path.abspath(__file__))
        output_directory: str = os.path.join(current_directory, f"./../results/devices/cycle-{generate_files_call_count}-{times_stamp}-noreport")

        os.makedirs(output_directory, exist_ok=True)
        return output_directory

    def generate_hash(self, *args: Union[str, int]) -> int:
        data: str = ''.join(map(str, args))
        return hash(data)
