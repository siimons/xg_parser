from src.parser.browser_manager import parse_data
from src.utils.config_loader import load_config_from_file

from src.utils.logger_setup import logger

def main():
    try:
        config = load_config_from_file()

        if not config:
            logger.error("Конфигурация пуста или невалидна.")
            raise ValueError("Конфигурация пуста или некорректна.")

        for item in config:
            try:
                parse_data(item["league"], item["gameweek"])
                logger.info(f"Завершена обработка для лиги '{item['league']}'")
                
            except Exception as e:
                logger.error(f"Ошибка в процессе для лиги '{item['league']}': {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Ошибка в работе приложения: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
