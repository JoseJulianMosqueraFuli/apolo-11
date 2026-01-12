<div align="center">

![Softserve](docs/images/softserve.png)

# 🚀 NASA Apollo 11 - Sistema de Simulación y Monitoreo

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/Poetry-gestión%20de%20dependencias-blue.svg)](https://python-poetry.org/)
[![Tests](https://img.shields.io/badge/Tests-45%20pasando-green.svg)](tests/)
[![Cobertura](https://img.shields.io/badge/Cobertura-98%25-brightgreen.svg)](htmlcov/)
[![Licencia](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](LICENSE)
[![Rich](https://img.shields.io/badge/TUI-Rich%20Dashboard-purple.svg)](https://rich.readthedocs.io/)

_Un sistema profesional de simulación y monitoreo para misiones espaciales NASA_

[English](README.md) • [Español](README.es.md)

</div>

---

## 📋 Tabla de Contenidos

- [Acerca de](#-acerca-de)
- [Características](#-características)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Dashboard](#-dashboard-tui)
- [Arquitectura](#-arquitectura)
- [Testing](#-testing)
- [Configuración](#-configuración)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

## 🎯 Acerca de

Apollo 11 es un sistema integral de simulación y monitoreo diseñado para misiones espaciales NASA. Construido con prácticas modernas de Python, proporciona capacidades de generación, análisis y reporte de datos de telemetría en tiempo real con una hermosa interfaz de usuario de terminal.

**Desarrollado como parte del Python Bootcamp Challenge de Softserve**, este proyecto demuestra conceptos avanzados de Python incluyendo:

- 🏗️ **Programación orientada a objetos** con clases y herencia
- 📁 **Operaciones de archivos** y gestión de directorios
- ⚙️ **Gestión de configuración** con YAML
- 🧪 **Testing integral** (tests unitarios + property-based testing)
- 🖥️ **Interfaz CLI** con parsing de argumentos
- 📊 **Dashboard en tiempo real** con librería Rich

El sistema simula escenarios del mundo real donde múltiples dispositivos en diferentes misiones espaciales generan datos de telemetría que necesitan ser recolectados, analizados y reportados en tiempo real.

## ✨ Características

Apollo 11 proporciona un conjunto completo de herramientas para el monitoreo de misiones espaciales:

### 🔧 Componentes Principales

- **📊 Generador de Datos**: Crea archivos de log simulados realistas para diferentes misiones y dispositivos
- **📈 Analizador de Reportes**: Procesa logs y genera estadísticas completas de estado de dispositivos
- **💾 Gestión de Backups**: Archiva automáticamente datos procesados con manejo inteligente de carpetas
- **🖥️ Dashboard TUI**: Hermosa interfaz de terminal para monitoreo en tiempo real usando la librería Rich

### 🚀 Capacidades Avanzadas

- **Monitoreo en Tiempo Real**: Actualizaciones en vivo del estado del sistema y estadísticas de misiones
- **Property-based Testing**: Validación robusta usando el framework Hypothesis
- **Logging Centralizado**: Sistema de logging configurable en todos los módulos
- **Alta Cobertura de Tests**: 98% de cobertura de tests con 45 tests integrales
- **CLI Profesional**: Sistema completo de parsing de argumentos con validación y ayuda

## Instalación

**Prerrequisitos:**

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)

```bash
# Clonar el repositorio
git clone git@github.com:JoseJulianMosqueraFuli/apolo-11.git
cd apolo-11

# Instalar dependencias
poetry install

# Activar entorno virtual
poetry shell
```

## Uso

### Ejecución básica

```bash
# Con valores por defecto
poetry run python main.py

# Con parámetros personalizados
poetry run python main.py --num_files_min 1 --num_files_max 100 --generator_interval 5 --reporter_interval 15

# Con dashboard habilitado para monitoreo en tiempo real
poetry run python main.py --dashboard
```

### Dashboard TUI

El sistema incluye un dashboard de Interfaz de Usuario Terminal (TUI) para monitoreo en tiempo real:

![Dashboard](docs/images/Dashboard.png)

**Características del dashboard:**

- Estado del sistema en tiempo real (archivos generados, ciclo actual, hora del último reporte)
- Estadísticas de misiones con conteos de dispositivos y resúmenes de estado
- Actualizaciones en vivo cada segundo
- Interfaz limpia y organizada usando la librería Rich

**Para habilitar el dashboard:**

```bash
poetry run python main.py --dashboard --generator_interval 3 --reporter_interval 10
```

### Parámetros CLI

| Parámetro              | Default | Descripción                                           |
| ---------------------- | ------- | ----------------------------------------------------- |
| `--num_files_min`      | 1       | Número mínimo de archivos log a generar por ciclo     |
| `--num_files_max`      | 100     | Número máximo de archivos log a generar por ciclo     |
| `--generator_interval` | 20      | Tiempo en segundos entre cada ciclo de generación     |
| `--reporter_interval`  | 60      | Tiempo en segundos entre cada ciclo de reportes       |
| `--dashboard`          | False   | Habilitar dashboard TUI para monitoreo en tiempo real |

**Nota:** El intervalo de reportes debe ser mayor que el intervalo del generador. El sistema ejecuta múltiples ciclos de generación antes de cada ciclo de reportes.

### Ejecutar tests

```bash
# Tests con cobertura
poetry run pytest --cov=apolo_11

# Tests verbose
poetry run pytest -v
```

## Estructura del Proyecto

```
apolo-11/
├── apolo_11/
│   ├── config/
│   │   └── config.yaml      # Configuración del sistema
│   └── src/
│       ├── classes.py       # Clases Mission y Device
│       ├── config.py        # ConfigManager
│       ├── dashboard.py     # Dashboard TUI con Rich
│       ├── generator.py     # Generador de logs
│       ├── logging_config.py # Logging centralizado
│       └── reporter.py      # Procesador de reportes
├── tests/
│   └── tests_src/           # Tests unitarios y de propiedades
├── docs/
│   └── images/              # Diagramas y documentación visual
├── main.py                  # Punto de entrada
└── pyproject.toml           # Dependencias del proyecto
```

## Arquitectura

![General](docs/images/general-diagram.png)

![Detalle](docs/images/DetailDiagram.png)

## Configuración

El archivo `apolo_11/config/config.yaml` contiene la configuración del sistema:

- Misiones disponibles y sus códigos
- Tipos de dispositivos y estados
- Rutas de directorios
- Formato de fechas
- Intervalos de generación/reporte

## Características del Dashboard

El Dashboard TUI proporciona capacidades de monitoreo en tiempo real:

### Panel de Resumen del Sistema

- **Archivos Generados**: Número total de archivos de log creados en la sesión actual
- **Ciclo Actual**: Número del ciclo de generación actual
- **Último Reporte**: Timestamp del reporte estadístico más reciente

### Panel de Estadísticas de Misiones

- **Nombre de Misión**: Misiones espaciales activas (GalaxyTwo, ColonyMoon, VacMars, etc.)
- **Tipos de Dispositivos**: Tipos de dispositivos por misión (Rover, Equipment, Sensor, etc.)
- **Total de Dispositivos**: Conteo de dispositivos por misión
- **Resumen de Estado**: Distribución de estados de dispositivos (operational, excellent, unknown, etc.)

### Actualizaciones en Tiempo Real

- El dashboard se actualiza automáticamente cada segundo
- Datos en vivo de los componentes generador y reporter
- Layout limpio y organizado usando la librería Rich
- Presiona `Ctrl+C` para salir correctamente

## Limitaciones Conocidas

- El intervalo de reportes siempre debe ser mayor que el intervalo del generador. Si los archivos se generan más rápido de lo que pueden procesarse, los datos pueden acumularse.
- El sistema no maneja acceso concurrente a archivos de log. No se soporta ejecutar múltiples instancias simultáneamente.
- El manejo de errores durante el procesamiento de archivos es básico; archivos de log malformados pueden causar problemas.

## Mejoras en Desarrollo

- ✅ Corrección de bugs en `move_folders_to_backup`
- ✅ Mejora de cobertura de tests
- ✅ Dashboard TUI con Rich
- ✅ Logging centralizado y configurable
- 🔄 Procesamiento paralelo con threads/async

## Licencia

Este proyecto está bajo la [Licencia MIT](LICENSE).

## Autores

Desarrollado por Alejandra Quiroz Gómez, Sara Palacio y Jose Julian Mosquera Fuli.
