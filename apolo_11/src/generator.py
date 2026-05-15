from dataclasses import dataclass

import os
import random
import uuid
from datetime import datetime

from .config import ConfigManager
from .classes import Mission, Device
from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class GeneratedFile:
    filename: str
    content: str


@dataclass
class DefaultContent:
    current_date: str
    mission_name: str
    device_type: str
    device_status: str
    hash_value: int

    def generate_content_string(self) -> str:
        return (
            f"Date: {self.current_date}\n"
            f"Mission: {self.mission_name}\n"
            f"Device Type: {self.device_type}\n"
            f"Device Status: {self.device_status}\n"
            f"Hash: {self.hash_value}"
        )


@dataclass
class CustomContent(DefaultContent):
    unique_id: str | None

    def generate_content_string(self) -> str:
        default_content = super().generate_content_string()
        return f"{default_content}\nID: {self.unique_id}" if self.unique_id else default_content


class Generator:
    def __init__(self, config_data: dict | None = None):
        if config_data is None:
            config_data = ConfigManager.read_yaml_config()
        self._config = config_data
        self.mission_instance = Mission(config_data=config_data)
        self.device_instance = Device(config_data=config_data)
        self.generate_files_call_count: int = 0

    def generate_device_folder(self, base_path: str = './apolo_11/results') -> None:
        folder_path = os.path.join(base_path, 'devices')
        os.makedirs(folder_path, exist_ok=True)

    def generate_filename(self, mission_name: str, file_number: int) -> str:
        mission_code: str = self._config['missions']['codes'].get(mission_name, 'UNKN')
        return f"APL{mission_code}-{file_number:04d}.log"

    def generate_contentfile(self, file_number: int) -> GeneratedFile:
        mission_name: str = random.choice(self.mission_instance.name)
        device_type: str = random.choice(self.device_instance.type)
        device_status: str = random.choice(self.device_instance.status)
        date_format: str = self._config['date_format']
        current_date: str = datetime.now().strftime(date_format)

        if mission_name in self._config['missions']['codes']:
            hash_value: int = self.generate_hash(current_date, mission_name, device_type, device_status)
            content = DefaultContent(current_date, mission_name,
                                     device_type, device_status,
                                     hash_value).generate_content_string()
        else:
            hash_value = 'unknown'
            device_status = 'unknown'
            device_type = 'unknown'
            unique_id = uuid.uuid4()
            content = CustomContent(current_date, mission_name,
                                    device_type, device_status,
                                    hash_value, unique_id).generate_content_string()

        filename = self.generate_filename(mission_name, file_number)
        return GeneratedFile(filename, content)

    def generate_files(self, num_files_min: int, num_files_max: int):
        try:
            self.load_cycle_number()
            times_stamp: str = datetime.now().strftime('%Y%m%d%H%M%S')
            output_directory: str = self.create_output_directory(times_stamp, self.generate_files_call_count)

            random_number: int = random.randint(num_files_min, num_files_max)
            for file_number in range(1, random_number + 1):
                generated_file = self.generate_contentfile(file_number)
                file_path: str = os.path.join(output_directory, generated_file.filename)
                with open(file_path, 'w') as file:
                    file.write(generated_file.content)
                logger.info("Archivo de misión creado: %s", os.path.basename(file_path))
                logger.info("Datos del archivo creado:\n%s", generated_file.content)

            self.save_cycle_number()

        except KeyboardInterrupt:
            logger.info("Generación de archivos interrumpida por teclado.")

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
        output_directory: str = os.path.join(
            current_directory,
            f"./../results/devices/cycle-{generate_files_call_count}-{times_stamp}-noreport")
        os.makedirs(output_directory, exist_ok=True)
        return output_directory

    def generate_hash(self, *args: str | int) -> int:
        data: str = ''.join(map(str, args))
        return hash(data)
