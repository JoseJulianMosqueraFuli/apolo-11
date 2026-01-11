![Softserve](docs/images/softserve.png)

# NASA Apollo 11 - Simulation and Monitoring System

A simulation and monitoring system for NASA space missions, developed as part of the Softserve Python Bootcamp Challenge.

## About This Project

This project was created as a learning exercise to practice Python development concepts including:

- Object-oriented programming with classes and inheritance
- File I/O operations and directory management
- Configuration management with YAML
- Unit testing and property-based testing
- CLI argument parsing

The system simulates a real-world scenario where multiple devices across different space missions generate telemetry data that needs to be collected, analyzed, and reported.

## Overview

Apollo 11 simulates device monitoring for space missions. It generates simulated telemetry data, analyzes logs, and produces real-time statistical reports.

**Main features:**

- Data generator: Creates simulated log files for different missions and devices
- Report analyzer: Processes logs and generates device status statistics
- Backup management: Automatically archives processed data
- TUI Dashboard: Terminal visual interface for real-time monitoring with Rich

## Installation

**Prerequisites:**

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)

```bash
# Clone the repository
git clone git@github.com:JoseJulianMosqueraFuli/apolo-11.git
cd apolo-11

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

## Usage

### Basic execution

```bash
# With default values
poetry run python main.py

# With custom parameters
poetry run python main.py --num_files_min 1 --num_files_max 100 --generator_interval 5 --reporter_interval 15

# With dashboard enabled for real-time monitoring
poetry run python main.py --dashboard
```

### Dashboard TUI

The system includes a Terminal User Interface (TUI) dashboard for real-time monitoring:

![Dashboard](docs/images/Dashboard.png)

**Dashboard features:**

- Real-time system status (files generated, current cycle, last report time)
- Mission statistics with device counts and status summaries
- Live updates every second
- Clean, organized interface using Rich library

**To enable the dashboard:**

```bash
poetry run python main.py --dashboard --generator_interval 3 --reporter_interval 10
```

### CLI Parameters

| Parameter              | Default | Description                                          |
| ---------------------- | ------- | ---------------------------------------------------- |
| `--num_files_min`      | 1       | Minimum number of log files to generate per cycle    |
| `--num_files_max`      | 100     | Maximum number of log files to generate per cycle    |
| `--generator_interval` | 20      | Time in seconds between each file generation cycle   |
| `--reporter_interval`  | 60      | Time in seconds between each report generation cycle |
| `--dashboard`          | False   | Enable TUI dashboard for real-time monitoring        |

**Note:** The reporter interval must be greater than the generator interval. The system runs multiple generation cycles before each report cycle.

### Run tests

```bash
# Tests with coverage
poetry run pytest --cov=apolo_11

# Verbose tests
poetry run pytest -v
```

## Project Structure

```
apolo-11/
├── apolo_11/
│   ├── config/
│   │   └── config.yaml      # System configuration
│   └── src/
│       ├── classes.py       # Mission and Device classes
│       ├── config.py        # ConfigManager
│       ├── dashboard.py     # TUI Dashboard with Rich
│       ├── generator.py     # Log generator
│       ├── logging_config.py # Centralized logging
│       └── reporter.py      # Report processor
├── tests/
│   └── tests_src/           # Unit and property tests
├── docs/
│   └── images/              # Diagrams and visual documentation
├── main.py                  # Entry point
└── pyproject.toml           # Project dependencies
```

## Architecture

![General](docs/images/general-diagram.png)

![Detail](docs/images/DetailDiagram.png)

## Configuration

The `apolo_11/config/config.yaml` file contains system configuration:

- Available missions and their codes
- Device types and statuses
- Directory paths
- Date formats
- Generation/report intervals

## Dashboard Features

The TUI Dashboard provides real-time monitoring capabilities:

### System Overview Panel

- **Files Generated**: Total number of log files created in the current session
- **Current Cycle**: Current generation cycle number
- **Last Report**: Timestamp of the most recent statistical report

### Mission Statistics Panel

- **Mission Name**: Active space missions (GalaxyTwo, ColonyMoon, VacMars, etc.)
- **Device Types**: Types of devices per mission (Rover, Equipment, Sensor, etc.)
- **Total Devices**: Count of devices per mission
- **Status Summary**: Device status distribution (operational, excellent, unknown, etc.)

### Real-time Updates

- Dashboard refreshes automatically every second
- Live data from generator and reporter components
- Clean, organized layout using Rich library
- Press `Ctrl+C` to exit gracefully

## Known Limitations

- The reporter interval must always be greater than the generator interval. If files are generated faster than they can be processed, data may accumulate.
- The system does not handle concurrent access to log files. Running multiple instances simultaneously is not supported.
- Error handling during file processing is basic; malformed log files may cause issues.

## Improvements in Progress

- ✅ Bug fixes in `move_folders_to_backup`
- ✅ Test coverage improvements
- ✅ TUI Dashboard with Rich
- ✅ Centralized and configurable logging
- 🔄 Parallel processing with threads/async

## License

This project is licensed under the [MIT License](LICENSE).

## Authors

Built by Alejandra Quiroz Gómez, Sara Palacio and Jose Julian Mosquera Fuli.
