import os
import json
from sys import stdout
from loguru import logger

CONFIG_PATH = os.path.join('config', 'logging_config.json')

with open(CONFIG_PATH, 'r') as config_file:
    config = json.load(config_file)

LOG_FILE_PATH = config.get("LOG_FILE_PATH", "logs/app.log")
LOG_LEVEL = config.get("LOG_LEVEL", "INFO")
LOG_ROTATION = config.get("LOG_ROTATION", "10 MB")
LOG_RETENTION = config.get("LOG_RETENTION", "7 days")

LOG_FORMAT_TERMINAL = (
    "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
    "<level>{level}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

LOG_FORMAT_FILE = (
    "{time:YYYY-MM-DD at HH:mm:ss} | {level} | "
    "{name}:{function}:{line} - {message}"
)

def configure_logger():
    """
    Конфигурирует логгер:
    - Удаляет стандартный логгер
    - Создаёт директорию для логов, если она не существует
    - Настраивает логирование в файл с ротацией и вывод в консоль с цветами
    """
    logger.remove()

    log_dir = os.path.dirname(os.path.abspath(LOG_FILE_PATH))
    if log_dir and not os.path.exists(log_dir):
        logger.debug(f"Creating log directory: {log_dir}")
        os.makedirs(log_dir, exist_ok=True)

    logger.add(
        LOG_FILE_PATH,
        rotation=LOG_ROTATION,
        retention=LOG_RETENTION,
        level=LOG_LEVEL,
        format=LOG_FORMAT_FILE,
        backtrace=True,  # Полный бэктрейс для ошибок
        diagnose=True    # Диагностика переменных
    )

    logger.add(
        stdout,
        level=LOG_LEVEL,
        format=LOG_FORMAT_TERMINAL,
        backtrace=True,
        diagnose=True,
        colorize=True
    )

    logger.info("Logger has been configured successfully.")

configure_logger()
__all__ = ['logger']