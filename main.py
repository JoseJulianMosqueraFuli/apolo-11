import argparse
import time

from apolo_11.src import generator, config, reporter

config_instance = config.ConfigManager()
config_data: dict = config_instance.read_yaml_config()

def main():
    parser = argparse.ArgumentParser(description='Generate files and generate reports for the Apolo 11 mission')
    parser.add_argument('--num_files_min', type=int, default=config_data['general']['num_files_initial'], help='Minimum number of files to generate')
    parser.add_argument('--num_files_max', type=int, default=config_data['general']['num_files_final'], help='Maximum number of files to generate')
    parser.add_argument('--generator_interval', type=int, default=config_data['general']['time_cycle'], help='Time interval in seconds for the generator')
    parser.add_argument('--reporter_interval', type=int, default=config_data['general']['time_cycle']*3, help='Time interval in seconds for the reporter')

    args = parser.parse_args()

    if args.reporter_interval <= args.generator_interval:
        print("Error: El intervalo de reportes debe ser mayor que el intervalo de generadores.")
        return

    generator_instance = generator.Generator()
    generator_instance.generate_device_folder()

    reporter_instance = reporter.Reporter()

    number_of_generator_iterations = round(int(args.reporter_interval/args.generator_interval))

    try:
        while True:
            for _ in range(number_of_generator_iterations):
                generator_instance.generate_files(
                    num_files_min=args.num_files_min,
                    num_files_max=args.num_files_max,
                )
                time.sleep(args.generator_interval)

            reporter_instance.process_files(config_data['routes']['devices'], config_data['routes']['backups'])
            reporter_instance.move_folders_to_backup(config_data['routes']['devices'], config_data['routes']['backups'])
            time.sleep(args.reporter_interval)

    except KeyboardInterrupt:
        print("Proceso interrumpido por el usuario.")

if __name__ == '__main__':
    main()
