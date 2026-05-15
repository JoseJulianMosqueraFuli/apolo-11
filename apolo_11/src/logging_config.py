"""
Centralized logging configuration module for Apollo 11 system.

Configures the 'apolo_11' logger with a StreamHandler.
Does NOT touch the root logger, safe to use as a library.
"""

import logging
from .config import ConfigManager


def setup_logging(config_path: str | None = None) -> logging.Logger:
    logger = logging.getLogger('apolo_11')

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)

    try:
        if config_path:
            config = ConfigManager.read_yaml_config(config_path)
        else:
            config = ConfigManager.read_yaml_config()

        logging_config = config.get('logging', {})
        log_level = logging_config.get('level', 'INFO')
        log_format = logging_config.get(
            'format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        logger.setLevel(getattr(logging, log_level.upper()))
        for handler in logger.handlers:
            handler.setFormatter(logging.Formatter(log_format))

    except Exception:
        logger.setLevel(logging.INFO)

    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f'apolo_11.{name}')
