"""
Centralized logging configuration module for Apollo 11 system.

This module provides a unified logging setup that reads configuration
from the YAML config file and ensures consistent logging format across
all modules.
"""

import logging
from typing import Optional
from .config import ConfigManager


def setup_logging(config_path: Optional[str] = None) -> logging.Logger:
    """
    Set up centralized logging configuration for the Apollo 11 system.

    Reads logging configuration from the YAML config file and sets up
    a consistent logging format across all modules.

    Args:
        config_path: Optional path to config file. If None, uses default.

    Returns:
        logging.Logger: Configured logger instance for the Apollo 11 system.
    """
    try:
        # Load configuration
        if config_path:
            config = ConfigManager.read_yaml_config(config_path)
        else:
            config = ConfigManager.read_yaml_config()

        # Get logging configuration with defaults
        logging_config = config.get('logging', {})
        log_level = logging_config.get('level', 'INFO')
        log_format = logging_config.get('format', 
                                       '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            force=True  # Override any existing configuration
        )

        # Create and return Apollo 11 specific logger
        logger = logging.getLogger('apolo_11')
        logger.setLevel(getattr(logging, log_level.upper()))

        return logger

    except Exception as e:
        # Fallback to basic logging if config fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger('apolo_11')
        logger.warning("Failed to load logging config, using defaults: %s", str(e))
        return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    This function ensures that all loggers use the centralized configuration
    set up by setup_logging().

    Args:
        name: Name for the logger, typically __name__ of the calling module.

    Returns:
        logging.Logger: Logger instance with the specified name.
    """
    return logging.getLogger(f'apolo_11.{name}')
