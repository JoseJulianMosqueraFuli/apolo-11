import os
import shutil

from datetime import datetime
from collections import defaultdict
from .config import ConfigManager
from .logging_config import get_logger

logger = get_logger(__name__)


class Reporter:
    def __init__(self, config_data: dict | None = None):
        if config_data is None:
            config_data = ConfigManager.read_yaml_config()
        self._config = config_data
        self.devices_reports = defaultdict(list)

    def generate_report_folder(self, base_path: str | None = None) -> None:
        base_path = base_path or self._config['routes']['results']
        for folder in ('backups', 'reports'):
            os.makedirs(os.path.join(base_path, folder), exist_ok=True)

    def process_files(self, input_directory: str, backup_directory: str) -> None:
        try:
            self.generate_report_folder()

            for root, _, files in os.walk(input_directory):
                for file in files:
                    if file.endswith(".log"):
                        self.process_file(os.path.join(root, file))

            self.generate_stats_report()
            self.move_folders_to_backup(input_directory, backup_directory)

        except Exception as e:
            logger.error("Error durante el procesamiento: %s", str(e))

    def move_folders_to_backup(self, source_directory: str | None = None,
                                backup_directory: str | None = None):
        source_directory = source_directory or self._config['routes']['devices']
        backup_directory = backup_directory or self._config['routes']['backups']

        for root, dirs, _ in os.walk(source_directory):
            for dir_name in dirs:
                if dir_name.endswith("-noreport"):
                    dest_name = dir_name[:-9]
                    shutil.move(
                        os.path.join(root, dir_name),
                        os.path.join(backup_directory, dest_name))

    def process_file(self, file_path: str) -> None:
        with open(file_path, 'r') as file:
            content = file.read()

        lines = content.split('\n')
        mission_name = self.extract_value(lines, "Mission")
        device_type = self.extract_value(lines, "Device Type")
        device_status = self.extract_value(lines, "Device Status")

        self.devices_reports[(mission_name, device_type)].append(device_status)
        logger.info("Mision '%s' y dispositivo '%s' registrada con éxito.", mission_name, device_type)

    @staticmethod
    def extract_value(lines: list[str], keyword: str) -> str:
        for line in lines:
            if keyword in line:
                parts = line.split(":")
                if len(parts) > 1:
                    return parts[1].strip()
                return "unknown"
        return "unknown"

    def generate_stats_report(self) -> None:
        stats_filename = f"APLSTATS-REPORT-{datetime.now().strftime(self._config['date_format'])}.log"
        stats_path = os.path.join(self._config['routes']['reports'], stats_filename)

        with open(stats_path, 'w') as stats_file:
            stats_file.write("Análisis de eventos:\n")
            for (mission, device_type), statuses in self.devices_reports.items():
                stats_file.write(f"Misión: {mission}, Tipo de Dispositivo: {device_type}\n")
                for status in set(statuses):
                    stats_file.write(f"   Estado: {status}, Cantidad: {statuses.count(status)}\n")

            stats_file.write("\nGestión de desconexiones:\n")
            for (mission, device_type), statuses in self.devices_reports.items():
                unknown_count = statuses.count("unknown")
                stats_file.write(f"Misión: {mission}, Tipo de Dispositivo: {device_type}\n")
                stats_file.write(f"   Desconexiones (unknown): {unknown_count}\n")

            stats_file.write("\nConsolidación de misiones:\n")
            total_unoperational = sum(1 for statuses in self.devices_reports.values() if "unknown" in statuses)
            stats_file.write(f"Total de dispositivos inoperables: {total_unoperational}\n")

            stats_file.write("\nCálculo de porcentajes:\n")
            for (mission, device_type), statuses in self.devices_reports.items():
                operational = len([s for s in statuses if s != "unknown"])
                percentage = operational / len(statuses) * 100
                stats_file.write(
                    f"Misión: {mission}, Tipo de Dispositivo: {device_type}, "
                    f"Porcentaje: {percentage:.2f}%\n")

        logger.info("Informe estadístico generado en: %s", stats_path)
