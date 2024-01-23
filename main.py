from apolo_11.src import generator, config

def main():
    config_instance = config.ConfigManager()
    
    generator_instance = generator.Generator()
    generator_instance.generate_principal_folders()
    # Only for testing purposes test with hardcode file
    generator_instance.generate_files(num_files_min=1, num_files_max=5)


if __name__ == '__main__':
    main()
