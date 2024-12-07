# Парсер футбольной статистики и прогнозов

Данный проект позволяет автоматически собирать статистику и прогнозы футбольных матчей с сайта [xGScore.io](https://xgscore.io/). Собранные данные, включая прогнозы счета, статистику команд и аналитические показатели, сохраняются в Excel-файл для удобного использования. Проект поддерживает гибкую настройку через файл конфигурации, что позволяет вам точно указать, какие данные необходимо собирать, адаптируя инструмент под ваши потребности.

## Структура проекта

```
xg_parser/
│
├── config/
│   ├── data_collection_settings.json
│   └── logging_config.json
│
├── data/
│   └── Spain. La Liga.xlsx
│
├── logs/
│   └── app.log
│
├── src/
│   ├── __init__.py
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── browser_manager.py
│   │   ├── data_collectors.py
│   │   └── user_agent.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config_loader.py
│       ├── excel_saver.py
│       └── logger_setup.py
│
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

## Используемые технологии

- **Selenium**: Библиотека для автоматизации веб-браузеров.
- **BeautifulSoup**: Библиотека для парсинга HTML и извлечения данных из веб-страниц.
- **openpyxl**: Модуль для работы с Excel-файлами.
- **loguru**: Логирование событий и ошибок.

## Установка

1. Клонируйте репозиторий

```bash
git clone https://github.com/siimons/xg_parser
cd xg_parser

```

2. Создайте и активируйте виртуальное окружение

```bash
python -m venv venv

source venv/bin/activate      # Для Linux/MacOS
venv\Scripts\activate         # Для Windows

```

3. Установите зависимости

```bash
pip install -r requirements.txt

```

4. Настройте параметры парсинга 

Отредактируйте файл `config/data_collection_settings.json` в соответствии с вашими требованиями. Пример структуры файла:

```json
[
    {
        "league": "Spain. La Liga",
        "gameweek": 5
    },
    {
        "league": "Norway. Eliteserien",
        "gameweek": [1, 6, 14, 18]
    }
]

```
5. Запустите программу

```bash
python main.py

```

## Логирование

Все ошибки и события записываются в файл logs/app.log. Формат логов позволяет отслеживать ход выполнения программы и быстро находить проблемы. Конфигурацию логирования вы можете изменить в файле `config/logging_config.json`.