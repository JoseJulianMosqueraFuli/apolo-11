<div align="center">

![Softserve](docs/images/softserve.png)

# 🚀 NASA Apollo 11 - Simulation and Monitoring System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/Poetry-dependency%20management-blue.svg)](https://python-poetry.org/)
[![CI](https://github.com/JoseJulianMosqueraFuli/apolo-11/actions/workflows/ci.yml/badge.svg)](https://github.com/JoseJulianMosqueraFuli/apolo-11/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/Tests-88%20passing-green.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-96%25-brightgreen.svg)](htmlcov/)
[![FastAPI](https://img.shields.io/badge/Web-FastAPI%20Dashboard-teal.svg)](https://fastapi.tiangolo.com/)
[![Kubernetes](https://img.shields.io/badge/K8s-Docker%20Desktop-blue.svg)](k8s/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

_A professional simulation and monitoring system for NASA space missions_

[English](README.md) • [Español](README.es.md)

</div>

---

## 📋 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Dashboard](#-dashboard-tui)
- [Architecture](#-architecture)
- [Testing](#-testing)
- [Configuration](#-configuration)
- [Contributing](#-contributing)
- [License](#-license)

## 🎯 About

Apollo 11 is a comprehensive simulation and monitoring system designed for NASA space missions. Built with modern Python practices, it provides real-time telemetry data generation, analysis, and reporting capabilities with a beautiful terminal user interface.

**Developed as part of the Softserve Python Bootcamp Challenge**, this project demonstrates advanced Python concepts including:

- 🏗️ **Object-oriented programming** with classes and inheritance
- 📁 **File I/O operations** and directory management
- ⚙️ **Configuration management** with YAML
- 🧪 **Comprehensive testing** (unit tests + property-based testing)
- 🖥️ **CLI interface** with argument parsing
- 📊 **Real-time dashboard** with Rich library
- 🌐 **Web dashboard** with FastAPI and auto-refresh
- ☸️ **Kubernetes** deployment with Ingress and RabbitMQ

The system simulates real-world scenarios where multiple devices across different space missions generate telemetry data that needs to be collected, analyzed, and reported in real-time.

## ✨ Features

Apollo 11 provides a complete suite of tools for space mission monitoring:

### 🔧 Core Components

- **📊 Data Generator**: Creates realistic simulated log files for different missions and devices
- **📈 Report Analyzer**: Processes logs and generates comprehensive device status statistics
- **💾 Backup Management**: Automatically archives processed data with intelligent folder handling
- **🖥️ TUI Dashboard**: Beautiful terminal interface for real-time monitoring using Rich library
- **🌐 Web Dashboard**: FastAPI web dashboard with JSON API, HTML interface, and Swagger docs

### 🚀 Advanced Capabilities

- **Real-time Monitoring**: Live updates of system status and mission statistics
- **Web Dashboard**: Auto-refreshing web UI with REST API and Swagger documentation
- **Property-based Testing**: Robust validation using Hypothesis framework
- **Centralized Logging**: Configurable logging system across all modules
- **High Test Coverage**: 96% test coverage with 88 comprehensive tests
- **Professional CLI**: Full argument parsing with validation and help system
- **Kubernetes Support**: Ready-to-deploy manifests for Docker Desktop

## 🛠️ Installation

### Prerequisites

- **Python 3.10+** - [Download here](https://www.python.org/downloads/)
- **Poetry** - [Installation guide](https://python-poetry.org/docs/#installation)

### Quick Start

#### Local

```bash
# 1. Clone the repository
git clone git@github.com:JoseJulianMosqueraFuli/apolo-11.git
cd apolo-11

# 2. Install dependencies
poetry install

# 3. Run with dashboard (recommended)
poetry run apolo --dashboard
```

#### Docker

```bash
# Build and run with RabbitMQ
docker compose up --build
```

### Verify Installation

```bash
# Run tests to verify everything works
poetry run pytest --cov=apolo_11 -v
```

## 🚀 Usage

### Basic Execution

```bash
# Default configuration
poetry run apolo

# Custom parameters
poetry run apolo --num_files_min 1 --num_files_max 100 --generator_interval 5 --reporter_interval 15

# Enable dashboard for real-time monitoring (recommended)
poetry run apolo --dashboard
```

### Command Line Parameters

| Parameter              | Default | Description                                          |
| ---------------------- | ------- | ---------------------------------------------------- |
| `--num_files_min`      | 1       | Minimum number of log files to generate per cycle    |
| `--num_files_max`      | 100     | Maximum number of log files to generate per cycle    |
| `--generator_interval` | 20      | Time in seconds between each file generation cycle   |
| `--reporter_interval`  | 60      | Time in seconds between each report generation cycle |
| `--dashboard`          | False   | Enable TUI dashboard for real-time monitoring        |
| `--api`                | False   | Enable web API dashboard (FastAPI)                   |
| `--api-port`           | 8000    | Port for the web API dashboard                       |

> **⚠️ Important:** The reporter interval must be greater than the generator interval to prevent data accumulation.

## 📊 Dashboard TUI

The system features a beautiful Terminal User Interface (TUI) dashboard built with the Rich library for real-time monitoring:

<div align="center">

![Dashboard](docs/images/Dashboard.png)

_Real-time monitoring dashboard with live statistics_

</div>

### 🎛️ Dashboard Features

#### System Overview Panel

- **📁 Files Generated**: Total log files created in current session
- **🔄 Current Cycle**: Active generation cycle number
- **⏰ Last Report**: Timestamp of most recent statistical report

#### Mission Statistics Panel

- **🚀 Mission Names**: Active space missions (GalaxyTwo, ColonyMoon, VacMars, etc.)
- **🔧 Device Types**: Device categories per mission (Rover, Equipment, Sensor, etc.)
- **📊 Device Counts**: Total devices per mission
- **✅ Status Summary**: Device status distribution (operational, excellent, unknown, etc.)

#### Real-time Updates

- ⚡ **Auto-refresh**: Updates every second automatically
- 📡 **Live Data**: Direct feed from generator and reporter components
- 🎨 **Clean Layout**: Professional interface using Rich library
- ⌨️ **Easy Exit**: Press `Ctrl+C` to exit gracefully

### Enable Dashboard

```bash
# Recommended settings for optimal dashboard experience
poetry run apolo --dashboard --generator_interval 3 --reporter_interval 10

# Enable web dashboard (also works alongside TUI)
poetry run apolo --api --api-port 8000

# Both together
poetry run apolo --dashboard --api --generator_interval 3 --reporter_interval 10
```

## 🌐 Web Dashboard

The system includes a modern web dashboard built with **FastAPI** for browser-based monitoring:

<div align="center">

### 🎛️ Endpoints

| Endpoint          | Description                                      |
| ----------------- | ------------------------------------------------ |
| `GET /`           | HTML dashboard with auto-refresh (every 3s)      |
| `GET /api/stats`  | JSON API with real-time system and mission stats |
| `GET /docs`       | Swagger UI for API exploration                   |

</div>

### Usage

```bash
# Enable the web dashboard
poetry run apolo --api --generator_interval 3 --reporter_interval 10

# Open in browser
open http://localhost:8000
```

The web dashboard displays the same real-time information as the TUI dashboard:

- **📁 Files Generated**: Total log files created in current session
- **🔄 Current Cycle**: Active generation cycle number
- **⏰ Last Report**: Timestamp of most recent statistical report
- **🚀 Mission Statistics**: Per-mission device counts and status breakdowns with color-coded badges
- **⚡ Auto-refresh**: Updates every 3 seconds via JavaScript fetch API
- **📡 REST API**: Machine-readable JSON at `/api/stats` for external integrations

## 🏗️ Architecture

The system follows a modular architecture with clear separation of concerns:

<div align="center">

![General Architecture](docs/images/general-diagram.png)

_High-level system architecture_

![Detailed Architecture](docs/images/DetailDiagram.png)

_Detailed component interactions_

</div>

### 📁 Project Structure

```
apolo-11/
├── 📁 apolo_11/
│   ├── 📁 config/
│   │   └── 📄 config.yaml      # System configuration
│   ├── 📁 src/
│   │   ├── 📄 classes.py       # Mission and Device classes
│   │   ├── 📄 cli.py           # Async CLI entry point
│   │   ├── 📄 config.py        # ConfigManager
│   │   ├── 📄 dashboard.py     # TUI Dashboard with Rich
│   ├── 📄 web_dashboard.py # Web Dashboard with FastAPI
│   │   ├── 📄 generator.py     # Log generator
│   │   ├── 📄 logging_config.py # Centralized logging
│   │   ├── 📄 messaging.py     # RabbitMQ message broker
│   │   └── 📄 reporter.py      # Report processor
│   └── 📁 results/             # Generated data (backups, reports)
├── 📁 tests/
│   └── 📁 tests_src/           # Unit and property tests (65+)
├── 📁 docs/
│   └── 📁 images/              # Diagrams and visual documentation
├── 📄 main.py                  # Backward-compatible entry point
├── 📁 k8s/                     # Kubernetes manifests
│   ├── 📄 apolo-configmap.yaml
│   ├── 📄 apolo-deployment.yaml
│   ├── 📄 apolo-pvc.yaml
│   ├── 📄 apolo-service.yaml
│   ├── 📄 rabbitmq-ingress.yaml
│   ├── 📄 rabbitmq-service.yaml
│   ├── 📄 rabbitmq-statefulset.yaml
│   └── 📄 README.md
├── 📄 Dockerfile               # Docker image build
├── 📄 docker-compose.yml       # Multi-service orchestration
└── 📄 pyproject.toml           # Project dependencies
```

## 🧪 Testing

The project maintains high code quality with comprehensive testing:

### Test Coverage

- **✅ 88 Tests Passing**: All tests pass consistently
- **📊 96% Coverage**: Excellent test coverage across all modules
- **🔬 Property-Based Testing**: Using Hypothesis for robust validation
- **🧪 Unit Testing**: Comprehensive unit tests for all components

### Run Tests

```bash
# Run all tests with coverage report
poetry run pytest --cov=apolo_11 --cov-report=term-missing --cov-report=html

# Run tests in verbose mode
poetry run pytest -v

# Run specific test file
poetry run pytest tests/tests_src/test_dashboard.py -v

# Generate HTML coverage report
poetry run pytest --cov=apolo_11 --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Types

- **Unit Tests**: Test individual components and functions
- **Property-Based Tests**: Test universal properties using Hypothesis
- **Integration Tests**: Test component interactions
- **Edge Case Tests**: Test error conditions and boundary cases

## ⚙️ Configuration

The system is highly configurable through the `apolo_11/config/config.yaml` file:

### Configuration Options

```yaml
# Mission definitions
missions:
  codes:
    OrbitOne: ORBONE
    GalaxyTwo: GALXTWO
  names:
    - OrbitOne
    - GalaxyTwo

# Device specifications
devices:
  types:
    - Satellite
    - Rover
  status:
    - excellent
    - good
    - warning

# System settings
general:
  num_files_initial: 1
  num_files_final: 100
  time_cycle: 20

# Logging configuration
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Directory paths
routes:
  results: ./apolo_11/results
  devices: ./apolo_11/results/devices
  backups: ./apolo_11/results/backups/
  reports: ./apolo_11/results/reports/
```

### Customization

- **Missions**: Add new space missions and their codes
- **Devices**: Define device types and status options
- **Logging**: Configure log levels and formats
- **Paths**: Customize directory structure
- **Intervals**: Set generation and reporting frequencies

## ⚠️ Known Limitations

- **Timing Constraints**: Reporter interval must exceed generator interval to prevent data accumulation
- **Concurrency**: No support for multiple simultaneous instances accessing the same log files
- **Error Handling**: Basic error handling for malformed log files may need enhancement
- **Resource Usage**: Large datasets may require additional memory optimization

## ☸️ Kubernetes

Deploy to any Kubernetes cluster (tested on Docker Desktop & Kind):

```bash
# Deploy everything
kubectl apply -f k8s/

# Watch pods
kubectl get pods -w
```

### Cluster Architecture

| Resource              | Description                                    |
| --------------------- | ---------------------------------------------- |
| `rabbitmq`            | StatefulSet + Service (AMQP 5672, Mgmt 15672)  |
| `apolo-11`            | Deployment with TUI + Web dashboard (port 8000) |
| `apolo-config`        | ConfigMap mounted at `/app/apolo_11/config/`    |
| `apolo-results`       | PVC for persistent mission data                 |
| `apolo-ingress`       | Ingress for `apolo.local` and `rabbitmq.local`  |

### Access

```bash
# Web dashboard
kubectl port-forward svc/apolo-11 8000:8000
# Open http://localhost:8000

# RabbitMQ management
kubectl port-forward svc/rabbitmq 15672:15672
# Open http://localhost:15672 (guest/guest)

# View logs
kubectl logs -l app=apolo-11 -f
```

See [`k8s/README.md`](k8s/README.md) for full instructions.

## 🐳 Docker

### Standalone container

```bash
docker build -t apolo-11 .
docker run --rm apolo-11 --dashboard --api --generator_interval 3 --reporter_interval 10
```

Mount a volume to persist results:

```bash
docker run --rm -v $(pwd)/results:/app/apolo_11/results -p 8000:8000 apolo-11 --api --generator_interval 3 --reporter_interval 10
```

### Docker Compose (with RabbitMQ)

```bash
docker compose up --build
```

Starts two services:

| Service    | Image                    | Ports                  |
| ---------- | ------------------------ | ---------------------- |
| `rabbitmq` | `rabbitmq:3-management`  | `5672` (AMQP)          |
|            |                          | `15672` (Management)   |
| `apolo-11` | (built from `Dockerfile`) | —                     |

The management UI is available at `http://localhost:15672` (guest/guest).

### Environment Variables

| Variable        | Default | Description                          |
| --------------- | ------- | ------------------------------------ |
| `RABBITMQ_HOST` | —       | RabbitMQ host. Unset = no messaging  |

## 📨 Message Broker (RabbitMQ)

When `RABBITMQ_HOST` is set, the generator publishes events to the `apolo.generated` topic exchange after each cycle:

```json
{
  "cycle": 5,
  "files_count": 50,
  "num_files_min": 1,
  "num_files_max": 10,
  "timestamp": "2026-05-14 20:00:00"
}
```

External consumers can subscribe to `apolo.generated` for real-time monitoring, dashboards, or archiving. The system works with full functionality when RabbitMQ is not available — messaging is optional and zero-overhead when disabled.

## 🚧 Recent Improvements

- ✅ **Web Dashboard**: FastAPI with auto-refresh HTML, JSON API, and Swagger docs
- ✅ **Kubernetes**: Service + Ingress for web dashboard and RabbitMQ
- ✅ **Architecture**: Eliminated side-effect imports — no IO at module load time
- ✅ **Dependency Injection**: All components accept optional config, testable without mocks
- ✅ **Config Stability**: Routes changed from fragile list indices to dict keys
- ✅ **Package Safety**: State file moved out of package source to results directory
- ✅ **CLI Entry Point**: `apolo` command works after `pip install` (no more `python main.py`)
- ✅ **CI/CD**: GitHub Actions with matrix testing across Python 3.10–3.12
- ✅ **Security**: Patched pytest (CVE-2024-11305) and Pygments (CVE-2024-43791)
- ✅ **Logging**: No longer stomps on root logger — safe as a library
- ✅ **SIGTERM Handling**: Graceful shutdown on kill signal
- 🔄 **Future**: Web dashboard with WebSocket real-time updates

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone git@github.com:yourusername/apolo-11.git
cd apolo-11

# Install development dependencies
poetry install

# Run tests before committing
poetry run pytest --cov=apolo_11 --cov-fail-under=95

# Run linting
poetry run flake8 apolo_11/
```

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

## 👥 Authors

<div align="center">

**Built with ❤️ by:**

🚀 **Alejandra Quiroz Gómez** • **Sara Palacio** • **Jose Julian Mosquera Fuli**

_Softserve Python Bootcamp Challenge_

---

<div align="center">

**⭐ Star this repository if you found it helpful!**

[🐛 Report Bug](https://github.com/JoseJulianMosqueraFuli/apolo-11/issues) • [✨ Request Feature](https://github.com/JoseJulianMosqueraFuli/apolo-11/issues) • [📖 Documentation](docs/)

</div>

</div>
