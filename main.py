import argparse
import time
from contextlib import nullcontext

from apolo_11.src import generator, reporter
from apolo_11.src.config import ConfigManager
from apolo_11.src.logging_config import setup_logging
from apolo_11.src.dashboard import Dashboard


def _extract_mission_stats(reporter_instance):
    missions = {}
    for (mission_name, device_type), statuses in reporter_instance.devices_reports.items():
        if mission_name not in missions:
            missions[mission_name] = {'device_counts': {}, 'status_counts': {}}

        if device_type in missions[mission_name]['device_counts']:
            missions[mission_name]['device_counts'][device_type] += len(statuses)
        else:
            missions[mission_name]['device_counts'][device_type] = len(statuses)

        for status in statuses:
            if status in missions[mission_name]['status_counts']:
                missions[mission_name]['status_counts'][status] += 1
            else:
                missions[mission_name]['status_counts'][status] = 1

    return missions


def main():
    logger = setup_logging()
    config_data = ConfigManager.read_yaml_config()

    parser = argparse.ArgumentParser(
        description='Generate files and generate reports for the Apolo 11 mission'
    )
    general_config = config_data['general']
    default_time_cycle = general_config['time_cycle']

    parser.add_argument('--num_files_min', type=int,
                        default=general_config['num_files_initial'],
                        help='Minimum number of files to generate')
    parser.add_argument('--num_files_max', type=int,
                        default=general_config['num_files_final'],
                        help='Maximum number of files to generate')
    parser.add_argument('--generator_interval', type=int,
                        default=default_time_cycle,
                        help='Time interval in seconds for the generator')
    parser.add_argument('--reporter_interval', type=int,
                        default=default_time_cycle * 3,
                        help='Time interval in seconds for the reporter')
    parser.add_argument('--dashboard', action='store_true',
                        help='Enable dashboard TUI for real-time monitoring')
    args = parser.parse_args()

    if args.num_files_min <= 0:
        parser.error('--num_files_min must be a positive integer')
    if args.num_files_max <= 0:
        parser.error('--num_files_max must be a positive integer')
    if args.num_files_min > args.num_files_max:
        parser.error('--num_files_min cannot be greater than --num_files_max')
    if args.generator_interval <= 0:
        parser.error('--generator_interval must be a positive integer')
    if args.reporter_interval <= 0:
        parser.error('--reporter_interval must be a positive integer')
    if args.reporter_interval <= args.generator_interval:
        logger.error("El intervalo de reportes debe ser mayor que el intervalo de generadores.")
        return

    generator_instance = generator.Generator(config_data=config_data)
    generator_instance.generate_device_folder()

    reporter_instance = reporter.Reporter(config_data=config_data)

    dashboard_instance = None
    live_display = None
    if args.dashboard:
        dashboard_instance = Dashboard()
        live_display = dashboard_instance.start_live_display()

    number_of_generator_iterations = round(int(args.reporter_interval / args.generator_interval))

    try:
        with live_display if live_display else nullcontext():
            while True:
                for iteration in range(number_of_generator_iterations):
                    generator_instance.generate_files(
                        num_files_min=args.num_files_min,
                        num_files_max=args.num_files_max,
                    )

                    if dashboard_instance:
                        generator_stats = {
                            'files_count': (iteration + 1) * args.num_files_max,
                            'cycle': generator_instance.generate_files_call_count,
                        }
                        reporter_stats = {
                            'missions': _extract_mission_stats(reporter_instance),
                            'last_report_time': getattr(reporter_instance, 'last_report_time', None),
                        }
                        dashboard_instance.update_stats(generator_stats, reporter_stats)
                        dashboard_instance.update_display()

                    time.sleep(args.generator_interval)

                reporter_instance.process_files(
                    config_data['routes']['devices'],
                    config_data['routes']['backups'],
                )

                if dashboard_instance:
                    from datetime import datetime
                    generator_stats = {
                        'files_count': number_of_generator_iterations * args.num_files_max,
                        'cycle': generator_instance.generate_files_call_count,
                    }
                    reporter_stats = {
                        'missions': _extract_mission_stats(reporter_instance),
                        'last_report_time': datetime.now(),
                    }
                    dashboard_instance.update_stats(generator_stats, reporter_stats)
                    dashboard_instance.update_display()

                time.sleep(args.reporter_interval)

    except KeyboardInterrupt:
        logger.info("Proceso interrumpido por el usuario.")
        if dashboard_instance:
            dashboard_instance.stop_display()


if __name__ == '__main__':
    main()
