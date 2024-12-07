import os
import json

from src.utils.logger_setup import logger

def load_config_from_file(config_path="config/data_collection_settings.json"):
    """
    Загружает параметры из файла конфигурации.
    :param config_path: Путь к файлу конфигурации.
    :return: Список словарей с конфигурацией.
    """
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                config = json.load(file)

                if isinstance(config, dict):
                    logger.info("Конфигурация представлена как одиночный объект. Преобразуем в список.")
                    config = [config]

                if not isinstance(config, list) or not all(isinstance(item, dict) for item in config):
                    raise ValueError("Формат конфигурации некорректен. Ожидается список объектов или один объект.")

                logger.info("Конфигурация успешно загружена из файла.")
                return config
        except json.JSONDecodeError as e:
            logger.warning(f"Ошибка в формате файла конфигурации: {e}")
        except FileNotFoundError:
            logger.warning("Файл конфигурации не найден.")
    else:
        logger.warning(f"Файл конфигурации не существует: {config_path}")
    return []