from dataclasses import dataclass
from typing import Union

import os
import random
import uuid
import logging
from datetime import datetime

from .config import ConfigManager
from .classes import Mission, Device

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('INFO: %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

config_path: str = 'apolo_11/config/config.yaml'
config: dict = ConfigManager.read_yaml_config(config_path)

@dataclass
class GeneratedFile:
    """Represents a generated log file
    Attributes:
        filename (str): The name of the generated log file
        content (str): The content of the generated log file    
    """
    filename: str
    content: str

class Generator:
    """Generate files with mission and devise data
    
    Attributes:
        mission_instance (Mission): instance of the Mission class
        device_instance (Device): instance of the Device class
        generate_files_call_count (int): number of times generate_files method is called
    
    """
    def __init__(self):
        self.mission_instance: Mission = Mission()
        self.device_instance: Device = Device()
        self.generate_files_call_count: int = 0

    def generate_device_folder(self, base_path='./apolo_11/results') -> None:
        """Generate folder for storing device files      
        
        """
        folder: str = 'devices'
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path, exist_ok=True)

    def generate_filename(self, mission_name, file_number) -> str:
        """Generate a filename for a log file

        Returns:
            str: generated file name
        """
        mission_code: str = config['missions']['codes'].get(mission_name, 'UNKN')
        return f"APL{mission_code}-{file_number:04d}.log"

    def generate_contentfile(self, file_number: int) -> str:
        """Generate content for a log file
        Returns:
            str: containing file name and file content        
        """
        
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

        return GeneratedFile(filename, content)

    def generate_files(self, num_files_min: int, num_files_max: int):
        """Generate log files with random data

        Args:
            num_files_min (int): Minimum number of files to generate
            num_files_max (int): Maximum number of files to generate
        """
        try:
            self.load_cycle_number()
            times_stamp: str = datetime.now().strftime('%Y%m%d%H%M%S')   
            output_directory: str = self.create_output_directory(times_stamp, self.generate_files_call_count)

            random_number: int = random.randint(num_files_min, num_files_max)

            for file_number in range(1, random_number + 1):
                generated_file = self.generate_contentfile(file_number)
                file_path: str = os.path.join(output_directory, generated_file.filename)

                with open(file_path, 'w') as file:
                    file.write(file_content)
            logger.info(f"Archivo de misión creado: {os.path.basename(file_path)}")
            logger.info(f"Datos del archivo creado:\n{file_content}")
            
            self.save_cycle_number()

        except KeyboardInterrupt:
            logger.info("Generación de archivos interrumpida por teclado.")

    def load_cycle_number(self):
        """
        Load generate_files_call_count from a file or
        set to 0 if not found
        """
        
        try:
            with open(os.path.join(os.path.dirname(__file__), 'cycle_number.txt'), 'r') as file:
                self.generate_files_call_count = int(file.read().strip())
        except FileNotFoundError:
            self.generate_files_call_count = 0
            self.save_cycle_number()

    def save_cycle_number(self):
        """
        Increment and save the generate_files_call_count to a file
        """
        self.generate_files_call_count += 1

        with open(os.path.join(os.path.dirname(__file__), 'cycle_number.txt'), 'w') as file:
            file.write(str(self.generate_files_call_count))

    def create_output_directory(self, times_stamp: str, generate_files_call_count: int) -> str:
        """Create the output directory path based on timestamp and call count        

        Args:
            times_stamp (str): timestamp for the output directory
            generate_files_call_count (int): call count for the output directory

        Returns:
            str: output directory path
        """
        current_directory: str = os.path.dirname(os.path.abspath(__file__))
        output_directory: str = os.path.join(current_directory, f"./../results/devices/cycle-{generate_files_call_count}-{times_stamp}-noreport")

        os.makedirs(output_directory, exist_ok=True)
        return output_directory

    def generate_hash(self, *args: Union[str, int]) -> int:
        """
        Generate hash number
        """
        data: str = ''.join(map(str, args))
        return hash(data)
