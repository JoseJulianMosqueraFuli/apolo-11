"""Property-based tests for project structure validation.

Feature: python-poetry-best-practices
"""

from pathlib import Path

import pytest


# Feature: python-poetry-best-practices, Property 18: Archivos __init__.py en paquetes
def test_all_python_packages_have_init_files():
    """
    Property 18: Archivos __init__.py en paquetes

    Para todos los directorios que contienen módulos Python (archivos .py),
    deben contener un archivo __init__.py para ser paquetes válidos.

    Validates: Requirements 8.4
    """
    project_root = Path(__file__).parent.parent.parent
    source_dir = project_root / "apolo_11"

    # Find all directories containing .py files
    directories_with_python_files = set()

    for py_file in source_dir.rglob("*.py"):
        if "__pycache__" not in str(py_file):
            directories_with_python_files.add(py_file.parent)

    # Check that each directory has an __init__.py
    for directory in directories_with_python_files:
        init_file = directory / "__init__.py"
        assert init_file.exists(), (
            f"Directory {directory.relative_to(project_root)} contains Python files "
            f"but is missing __init__.py"
        )


# Feature: python-poetry-best-practices, Property 20: Archivos de configuración en raíz
def test_configuration_files_in_root():
    """
    Property 20: Archivos de configuración en raíz

    Para cualquier proyecto, los archivos de configuración (pyproject.toml,
    .pre-commit-config.yaml, pytest.ini, .gitignore) deben estar en el
    directorio raíz.

    Validates: Requirements 8.5
    """
    project_root = Path(__file__).parent.parent.parent

    # Required configuration files
    required_files = [
        "pyproject.toml",
        ".gitignore",
    ]

    # Optional but recommended configuration files
    recommended_files = [
        ".pre-commit-config.yaml",
        "pytest.ini",  # Can also be in pyproject.toml
    ]

    # Check required files exist in root
    for filename in required_files:
        file_path = project_root / filename
        assert file_path.exists(), (
            f"Required configuration file {filename} not found in project root"
        )

    # Check that configuration files are not in subdirectories
    # Directories to ignore (build outputs, caches, etc.)
    ignore_dirs = {'htmlcov', 'dist', 'build', '.pytest_cache', '.mypy_cache',
                   '.ruff_cache', '__pycache__', 'node_modules', '.hypothesis'}

    for config_file in required_files + recommended_files:
        # Search for the file in subdirectories (excluding .git, node_modules, etc.)
        for found_file in project_root.rglob(config_file):
            if found_file.parent != project_root:
                # Ignore files in hidden directories or common ignore patterns
                relative_path = found_file.relative_to(project_root)
                # Check if any part of the path is in ignore_dirs or starts with '.'
                if not any(part.startswith('.') or part in ignore_dirs
                           for part in relative_path.parts[:-1]):
                    pytest.fail(
                        f"Configuration file {config_file} found in subdirectory: "
                        f"{found_file.relative_to(project_root)}"
                    )
