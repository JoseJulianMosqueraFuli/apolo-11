import os
import logging
import shutil

from datetime import datetime
from collections import defaultdict
from typing import List
from .config import ConfigManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('INFO: %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

config = ConfigManager.read_yaml_config()


class Reporter:
    """
    Generate reports based on log files

    Attributes:
        devices_reports (defaultdict): List to store reports categorized
        by mission and device type.
    """
    def __init__(self) -> None:
        self.devices_reports = defaultdict(list)

    def generate_report_folder(self, base_path=None) -> None:
        """
        Generate folders for storing backup and report files

        """
        base_path = base_path or config['routes'][0]['results']
        folders: list[str] = ['backups', 'reports']
        for folder in folders:
            folder_path = os.path.join(base_path, folder)
            os.makedirs(folder_path, exist_ok=True)

    def process_files(self, input_directory: str, backup_directory: str) -> None:
        """
        Process log files, generate reports, and move folders to backup
        """
        try:
            self.generate_report_folder()

            for root, dirs, files in os.walk(input_directory):
                for file in files:
                    if file.endswith(".log"):
                        file_path = os.path.join(root, file)
                        self.process_file(file_path)

            self.generate_stats_report()

            self.move_folders_to_backup(input_directory, backup_directory)

        except Exception as e:
            logger.error(f"Error durante el procesamiento: {e}")

    def move_folders_to_backup(self, source_directory=None, backup_directory=None):
        """
        Move folders with noreport to backup directory

        Args:
            source_directory: Source directory containing folders to be moved.
                            If None, uses config default (results/devices).
            backup_directory: Backup directory to move folders to.
                            If None, uses config default (results/backups).
        """
        source_directory = source_directory or config['routes'][1]['devices']
        backup_directory = backup_directory or config['routes'][2]['backups']

        for root, dirs, files in os.walk(source_directory):
            for dir_name in dirs:
                if dir_name.endswith("-noreport"):
                    source_dir = os.path.join(root, dir_name)
                    dest_dir_name = dir_name[:-9]  # Remove "-noreport" suffix
                    dest_dir = os.path.join(backup_directory, dest_dir_name)
                    shutil.move(source_dir, dest_dir)

    def process_file(self, file_path: str) -> None:
        """
        Process a log file and extract relevant information
        """
        with open(file_path, 'r') as file:
            content = file.read()

        lines = content.split('\n')
        mission_name = self.extract_value(lines, "Mission")
        device_type = self.extract_value(lines, "Device Type")
        device_status = self.extract_value(lines, "Device Status")

        self.devices_reports[(mission_name, device_type)].append(device_status)

        logger.info(f"Mision '{mission_name}' y dispositivo '{device_type}' registrada con éxito.")

    def extract_value(self, lines: List[str], keyword: str) -> str:
        """
        Extract a value from lines containing a specific keyword

        Args:
            lines(List): list of lines to search for the keyword
            keyword (str): keyword to search

        Returns:
        The extracted value or "unknown" if not found
        """
        for line in lines:
            if keyword in line:
                return line.split(":")[1].strip()
        return "unknown"

    def generate_stats_report(self) -> None:
        """
        Generate a stats report based on processed log files
        """
        stats_filename = f"APLSTATS-REPORT-{datetime.now().strftime(config['date_format'])}.log"
        stats_path = os.path.join(config['routes'][3]['reports'], stats_filename)

        with open(stats_path, 'w') as stats_file:
            # Analysis
            stats_file.write("Análisis de eventos:\n")
            for (mission, device_type), statuses in self.devices_reports.items():
                stats_file.write(f"Misión: {mission}, Tipo de Dispositivo: {device_type}\n")
                for status in set(statuses):
                    count = statuses.count(status)
                    stats_file.write(f"   Estado: {status}, Cantidad: {count}\n")

            # Management
            stats_file.write("\nGestión de desconexiones:\n")
            for (mission, device_type), statuses in self.devices_reports.items():
                unknown_count = statuses.count("unknown")
                stats_file.write(f"Misión: {mission}, Tipo de Dispositivo: {device_type}\n")
                stats_file.write(f"   Desconexiones (unknown): {unknown_count}\n")

            # Consolidation
            stats_file.write("\nConsolidación de misiones:\n")
            total_unoperational = sum(1 for statuses in self.devices_reports.values() if "unknown" in statuses)
            stats_file.write(f"Total de dispositivos inoperables: {total_unoperational}\n")

            # Percentage
            stats_file.write("\nCálculo de porcentajes:\n")
            for (mission, device_type), statuses in self.devices_reports.items():
                percentage = len([status for status in statuses if status != "unknown"]) / len(statuses) * 100
                stats_file.write(
                    f"Misión: {mission}, Tipo de Dispositivo: {device_type}, "
                    f"Porcentaje: {percentage:.2f}%\n")

        logger.info(f"Informe estadístico generado en: {stats_path}")
