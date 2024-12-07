import time
import random

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.parser.user_agent import get_random_user_agent
from src.parser.data_collectors import (
    parse_xg_statistics,
    parse_preview,
    collect_match_score_prediction
)

from src.utils.excel_saver import save_data_to_excel
from src.utils.logger_setup import logger

def random_delay(min_sec=2, max_sec=5):
    """Добавляет случайную задержку."""
    time.sleep(random.uniform(min_sec, max_sec))

def init_driver():
    """
    Инициализирует Selenium WebDriver с настройками для обхода антибот-защиты.
    :return: WebDriver объект.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f'user-agent={get_random_user_agent()}')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => false});"
    })
    driver.execute_script("delete window.navigator.__proto__.webdriver;")
    
    driver.maximize_window()
    logger.info("WebDriver успешно инициализирован.")
    
    return driver

def navigate_to_league_and_gameweek(driver, league_name, gameweek):
    """
    Переходит на страницу лиги и выбирает нужную игровую неделю.
    :param driver: WebDriver объект.
    :param league_name: Название лиги (например, "La Liga").
    :param gameweek: Номер игровой недели.
    """
    base_url = "https://xgscore.io/xg-statistics/"
    driver.get(base_url)
    logger.info("Открыта главная страница статистики.")

    try:
        random_delay()
        league_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "li.xgs-sidebar-nav_item a"))
        )

        leagues = driver.find_elements(By.CSS_SELECTOR, "li.xgs-sidebar-nav_item a")
        league_found = False
        for league in leagues:
            if league_name.lower() in league.text.lower():
                random_delay()
                league.click()
                league_found = True
                logger.info(f"Лига '{league_name}' выбрана.")
                break

        if not league_found:
            raise ValueError(f"Лига '{league_name}' не найдена.")

    except Exception as e:
        logger.error(f"Ошибка при выборе лиги '{league_name}': {e}")
        logger.warning(f"Программа остановлена на лиге '{league_name}', неделя {gameweek}.")
        raise

    try:
        random_delay()
        week_dropdown_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#mat-select-value-5 > span > span"))
        )
        week_dropdown_icon.click()
        logger.info("Открыт список игровых недель.")

        random_delay()
        gameweeks = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".mat-option"))
        )

        gameweek_found = False
        for gw in gameweeks:
            logger.info(gw.text)
            
            if f"{gameweek} Gameweek" in gw.text:
                random_delay()
                gw.click()
                gameweek_found = True
                logger.info(f"Игровая неделя {gameweek} выбрана.")
                break

        if not gameweek_found:
            raise ValueError(f"Игровая неделя {gameweek} не найдена.")

    except Exception as e:
        logger.error(f"Ошибка при выборе игровой недели '{gameweek}': {e}")
        logger.warning(f"Программа остановлена на лиге '{league_name}', неделя {gameweek}.")
        raise

def parse_statistics_data(driver, league_name):
    """
    Парсит данные матчей с текущей страницы, переходя по каждой ссылке матча.
    Собирает информацию с вкладок xg-statistics и preview.
    :param driver: WebDriver объект.
    :param league_name: Название лиги (например, "La Liga").
    """
    random_delay()
    soup = BeautifulSoup(driver.page_source, "lxml")
    logger.info("HTML страницы загружен и передан в BeautifulSoup.")

    links = [
        "https://xgscore.io" + block.find("a")["href"]
        for block in soup.find_all("xgs-xg-game-fixture", class_="xgs-panel ng-star-inserted")
    ]
    logger.info(f"Найдено {len(links)} матчей для парсинга.")

    for idx, link in enumerate(links):
        try:
            logger.info(f"Переход по ссылке {idx + 1}/{len(links)}: {link}")
            driver.get(link)
            random_delay()

            soup = BeautifulSoup(driver.page_source, "lxml")
            logger.info("Парсинг данных с вкладки xg-statistics.")
            xg_data = parse_xg_statistics(soup)

            try:
                preview_tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".xgs-tab_link[href*='/preview']"))
                )
                random_delay()
                preview_tab.click()
                logger.info("Переключение на вкладку preview.")
                
                random_delay()
                soup = BeautifulSoup(driver.page_source, "lxml")
                logger.info("Парсинг данных с вкладки preview.")
                preview_data = parse_preview(soup)

                logger.info("Сбор данных о прогнозах счета матча.")
                match_score_prediction = collect_match_score_prediction(driver)

            except Exception as e:
                logger.error(f"Ошибка при переключении на вкладку preview: {e}")
                preview_data = {}
                match_score_prediction = {}

            statistic = {
                "preview": preview_data,
                "match_score_prediction": match_score_prediction,
                "xg_statistics": xg_data,
            }
            
            logger.info(f"Данные матча собраны: {statistic}")
            
            save_data_to_excel(statistic, league_name)
            logger.info(f"Данные сохранены для матча: {link}")

        except Exception as e:
            logger.error(f"Ошибка при парсинге данных матча по ссылке {link}: {e}")
            logger.warning(f"Программа остановилась на матче {idx + 1}/{len(links)}: {link}.")
            continue

def parse_data(league_name, gameweeks):
    """
    Основная функция для парсинга данных. Обрабатывает как одиночные, так и множественные игровые недели.
    :param league_name: Название лиги.
    :param gameweeks: Список игровых недель или одно число.
    """
    if isinstance(gameweeks, int):
        gameweeks = [gameweeks]

    driver = init_driver()
    try:
        for gameweek in gameweeks:
            try:
                logger.info(f"Начало парсинга для лиги '{league_name}' и игровой недели {gameweek}.")
                navigate_to_league_and_gameweek(driver, league_name, gameweek)
                parse_statistics_data(driver, league_name)
            except Exception as e:
                logger.error(f"Ошибка при обработке недели {gameweek} для лиги '{league_name}': {e}", exc_info=True)
    finally:
        driver.quit()
        logger.info("WebDriver закрыт.")
