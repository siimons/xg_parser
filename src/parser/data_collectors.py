from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.utils.logger_setup import logger

def parse_xg_statistics(soup):
    """
    Собирает данные с вкладки xg-statistics.
    :param soup: Объект BeautifulSoup текущей страницы.
    :return: Словарь с данными вкладки xg-statistics.
    """
    try:
        rows = soup.find_all("div", class_="xgs-game-statistics-details-row")
        
        if len(rows) < 2:
            logger.warning("Недостаточно строк для xg-statistics.")
            return {
                "goals_team_1": None,
                "goals_team_2": None,
                "expected_goals_team_1": None,
                "expected_goals_team_2": None,
            }

        goals_row = rows[0]
        goals_team_1 = goals_row.find("strong", class_="text-primary")
        goals_team_2 = goals_row.find("strong", class_="text-secondary")

        xg_row = rows[1]
        xg_team_1 = xg_row.find("strong", class_="text-primary")
        xg_team_2 = xg_row.find("strong", class_="text-secondary")

        data = {
            "goals_team_1": goals_team_1.text.strip() if goals_team_1 else None,
            "goals_team_2": goals_team_2.text.strip() if goals_team_2 else None,
            "expected_goals_team_1": xg_team_1.text.strip() if xg_team_1 else None,
            "expected_goals_team_2": xg_team_2.text.strip() if xg_team_2 else None,
        }

        logger.info(f"Данные с xg-statistics собраны: {data}")
        return data

    except Exception as e:
        logger.error(f"Ошибка при парсинге вкладки xg-statistics: {e}")
        return {
            "goals_team_1": None,
            "goals_team_2": None,
            "expected_goals_team_1": None,
            "expected_goals_team_2": None,
        }

def parse_preview(soup):
    """
    Собирает данные с вкладки preview.
    :param soup: Объект BeautifulSoup текущей страницы.
    :return: Словарь с данными вкладки preview.
    """
    try:
        data = {}

        # Teams
        team_name_1 = soup.find("div", class_="mx-4 mx-lg-3 mx-xs-1 text-md-center my-md-1")
        data["team_name_1"] = team_name_1.find("strong", class_="xgs-game-header_team-name").text.strip() if team_name_1 else ""

        team_name_2 = soup.find("div", class_="mx-4 mx-lg-3 mx-xs-1 text-right text-md-center my-md-1")
        data["team_name_2"] = team_name_2.find("strong", class_="xgs-game-header_team-name").text.strip() if team_name_2 else ""

        # Predictions
        card_1 = soup.find("div", class_="xgs-category-forecast-card_header")
        if card_1:
            winner = card_1.find("p", class_="bold-text text-medium text-sm-small")
            xg_mark = card_1.find("span", class_="text-medium text-sm-tiny")
            data["winner"] = f"{winner.text.strip() if winner else ''} ({xg_mark.text.strip() if xg_mark else ''})"

        card_2 = soup.find_all("div", class_="xgs-category-forecast-card_header")
        if len(card_2) > 1:
            total_under_label = card_2[1].find("p", class_="bold-text text-medium text-sm-small")
            total_under_mark = card_2[1].find("span", class_="text-medium text-sm-tiny")
            data["total_under"] = f"{total_under_label.text.strip() if total_under_label else ''} ({total_under_mark.text.strip() if total_under_mark else ''})"

        card_3 = soup.find("div", class_="col-3 col-lg-6 m-xs-0 p-xs-0 ng-star-inserted")
        if card_3:
            both_to_score = card_3.find("p", class_="bold-text text-medium text-sm-small")
            both_to_score_mark = card_3.find("span", class_="text-medium text-sm-tiny")
            data["both_to_score"] = f"{both_to_score.text.strip() if both_to_score else ''} ({both_to_score_mark.text.strip() if both_to_score_mark else ''})"

        card_4 = soup.find_all("div", class_="col-3 col-lg-6 m-xs-0 p-xs-0 ng-star-inserted")
        if len(card_4) > 1:
            correct_score = card_4[1].find("p", class_="bold-text text-medium text-sm-small")
            correct_score_mark = card_4[1].find("span", class_="text-medium text-sm-tiny")
            data["correct_score"] = f"{correct_score.text.strip() if correct_score else ''} ({correct_score_mark.text.strip() if correct_score_mark else ''})"

        # Key Stats
        blocks = soup.find_all("div", class_="mb-6")
        logger.info(f"Найдено {len(blocks)} блоков с классом 'mb-6'.")

        if blocks:
            team_rating_home = blocks[0].find_all("span", class_="text-sm-small ng-star-inserted")
            if len(team_rating_home) >= 2:
                data["team_rating_home"] = team_rating_home[0].text.strip()
                data["team_rating_away"] = team_rating_home[1].text.strip()

        if len(blocks) > 1:
            team_form_home = blocks[1].find_all("span", class_="text-sm-small ng-star-inserted")
            if len(team_form_home) >= 2:
                data["team_form_home"] = team_form_home[0].text.strip()
                data["team_form_away"] = team_form_home[1].text.strip()

        if len(blocks) > 2:
            xg_luckiness = blocks[-1].find_all("span", class_="text-sm-small ng-star-inserted")
            if len(xg_luckiness) >= 2:
                data["xg_luckiness_home"] = xg_luckiness[0].text.strip()
                data["xg_luckiness_away"] = xg_luckiness[1].text.strip()

        block_4 = soup.find("div", class_="mb-3 ng-star-inserted")
        if block_4:
            predictability_values = block_4.find_all("span", class_="text-sm-small ng-star-inserted")
            if len(predictability_values) > 1:
                data["xg_predictability_home"] = predictability_values[0].text.strip()
                data["xg_predictability_away"] = predictability_values[1].text.strip()

        row_1 = soup.find("xgs-recent-goals-bar-group", class_="ng-star-inserted")
        if row_1:
            avg_xg_scored = row_1.find("div", class_="mb-6")
            if avg_xg_scored:
                values = avg_xg_scored.find_all("span", class_="text-sm-small ng-star-inserted")
                if len(values) > 1:
                    data["avg_xg_scored_home"] = values[0].text.strip()
                    data["avg_xg_scored_away"] = values[1].text.strip()

        row_2 = soup.find("xgs-recent-goals-bar-group", class_="ng-star-inserted")
        if row_2:
            avg_xg_conceded = row_2.find("div", class_="mb-3")
            if avg_xg_conceded:
                values = avg_xg_conceded.find_all("span", class_="text-sm-small ng-star-inserted")
                if len(values) > 1:
                    data["avg_xg_conceded_home"] = values[0].text.strip()
                    data["avg_xg_conceded_away"] = values[1].text.strip()

        logger.info(f"Данные с вкладки preview собраны: {data}")
        return data

    except Exception as e:
        logger.error(f"Ошибка при парсинге вкладки preview: {e}")
        return {}

def collect_match_score_prediction(driver):
    """
    Собирает информацию о прогнозах счета матча (Match Score Prediction) с помощью Selenium.
    :param driver: WebDriver объект.
    :return: Словарь с данными прогноза счета.
    """
    try:
        prediction_block = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[id*='xgs-game-result']"))
        )
        logger.info("Найден блок с прогнозом счета.")
        
        marks = prediction_block.find_elements(By.CSS_SELECTOR, "mark.xgs-mark.-huge strong")
        logger.info(f"Найдено {len(marks)} элементов с прогнозами.")

        if len(marks) >= 2:
            return {
                "match_score_prediction_home": marks[0].text.strip(),
                "match_score_prediction_away": marks[1].text.strip(),
            }
            
        logger.warning("Недостаточно данных для прогноза счета.")
        return {}

    except Exception as e:
        logger.error(f"Ошибка при сборе данных о прогнозах счета: {e}")
        return {}
