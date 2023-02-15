import os
import logging

from src.synapse.common.variables import (
    log_format,
    time_format,
    project_root_dir,
)


def logger_setup(
        log_name: str,
        filename: str,
        level=logging.INFO,
) -> logging.Logger:
    """
    Sets up a new logger config.

    :param log_name: Name of Logger. Make sure unique name is given for each Log
    :param filename: Name of filename
    :param level: Logger level of severity
    :returns: An instance of the Logger class
    """
    # Set up formatting style
    formatter = logging.Formatter(log_format, datefmt=time_format)

    handler = logging.FileHandler(filename)
    handler.setFormatter(formatter)

    # Create logger with name, level and handler
    logger = logging.getLogger(log_name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


try:
    # Create a Logger class instance
    log_file = logger_setup("error", f"{project_root_dir}/logs/error.log")

    log_error = logger_setup("error", f"{project_root_dir}/logs/error.log")
    log_telegram = logger_setup("telegram", f"{project_root_dir}/logs/telegram.log")
    log_arbitrage = logger_setup("arbitrage", f"{project_root_dir}/logs/arbitrage.log")

except FileNotFoundError:
    # If ./logs directory does not exist, create one
    a = os.system(f'mkdir {project_root_dir}/logs')

    # Create a Logger class instance
    log_error = logger_setup("error", f"{project_root_dir}/logs/error.log")
    log_telegram = logger_setup("telegram", f"{project_root_dir}/logs/telegram.log")
    log_arbitrage = logger_setup("arbitrage", f"{project_root_dir}/logs/arbitrage.log")
    