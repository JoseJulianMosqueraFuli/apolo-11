import argparse
import time

from apolo_11.src import generator, config, reporter

# Nitpick: find a way to import this from .yaml
config_path: str = 'apolo_11/config/config.yaml'
config_instance = config.ConfigManager()
config_data: dict = config_instance.read_yaml_config(config_path)

def main():
    parser = argparse.ArgumentParser(description='Generate files and generate reports for the Apolo 11 mission')
    parser.add_argument('--num_files_min', type=int, default=1, help='Minimum number of files to generate')
    parser.add_argument('--num_files_max', type=int, default=5, help='Maximum number of files to generate')
    parser.add_argument('--generator_interval', type=int, default=5, help='Time interval in seconds for the generator')
    parser.add_argument('--reporter_interval', type=int, default=15, help='Time interval in seconds for the reporter')

    args = parser.parse_args()

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

            reporter_instance.process_files("./apolo_11/results/devices", "./apolo_11/results/backups")
            reporter_instance.move_folders_to_backup("./apolo_11/results/devices", "./apolo_11/results/backups")
            time.sleep(args.reporter_interval)

    except KeyboardInterrupt:
        print("Proceso interrumpido por el usuario.")
    
if __name__ == '__main__':
    main()
