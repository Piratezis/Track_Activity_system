"""
Конфигурационные настройки для системы анализа социальных сетей
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

# 📁 Директории и пути
BASE_DIR = Path(__file__).parent.parent
STORAGE_DIR = BASE_DIR / "storage"
LOG_DIR = BASE_DIR / "logs"

# Создаем необходимые директории
for directory in [STORAGE_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# 🔑 Ключи социальных сетей
TELEGRAM_KEY = "telegram"
SLACK_KEY = "slack"
VK_KEY = "vk"
WHATSAPP_KEY = "whatsapp"

SOCIAL_NETWORK_DICT = {
    TELEGRAM_KEY: "telegram",
    SLACK_KEY: "slack",
    VK_KEY: "vkontakte",
    WHATSAPP_KEY: "whatsApp",
}

# 👤 Пользовательские настройки
# 👤 Пользовательские настройки (из .env)
DEFAULT_USERNAME = os.getenv("DEFAULT_USERNAME", "Пользователь")
PHONE_NUMBERS = [os.getenv("TELEGRAM_PHONE_NUMBER")]

# Настройки чатов (из .env)
DEFAULT_CHAT_NAME = os.getenv("DEFAULT_CHAT_NAME")
CHAT_URLS = os.getenv("CHAT_URLS", "").split(",")

# Временные настройки (из .env)
LOG_ROTATION_SIZE = int(os.getenv("LOG_ROTATION_SIZE", 524288000))
MESSAGE_FETCH_LIMIT = int(os.getenv("MESSAGE_FETCH_LIMIT", 1000))


# Telegram API настройки
# TELEGRAM_API = {
#     "SESSION_TEMPLATE": "{phone_number}_session",
#     "APP_VERSION": ,
#     "DEVICE_MODEL": ,
#     "SYSTEM_VERSION": ,
#     "LANG_CODE": ,
#     "SYSTEM_LANG_CODE": ,
# }
class CommandLineArgument:
    FLAG = "--"

    # unloading_of_chats.py
    USER_SYSTEM_NAME = FLAG + "user_system_name"
    API_HASH = FLAG + "api_hash"
    API_ID = FLAG + "api_id"
    SOCIAL_ACCOUNT_NAME = FLAG + "social_account_name"
    CHAT_NAME = FLAG + "chat_name"
    PHONE = FLAG + "phone"
    OUTPUT = FLAG + "output"

    # analysis_chts.py
    FILE = FLAG + "file"
    DATE = FLAG + "date"

    USER_SYSTEM_NAME_ANALYSIS = USER_SYSTEM_NAME
    SOCIAL_ACCOUNT_NAME_ANALYSIS = SOCIAL_ACCOUNT_NAME
    CHAT_NAME_ANALYSIS = CHAT_NAME
    PHONE_ANALYSIS = PHONE
    OUTPUT_ANALYSIS = OUTPUT

    # send_report.py
    PDF = FLAG + "pdf"
    TO = FLAG + "to"
    SUBJECT = FLAG + "subject"
    BODY = FLAG + "body"


class SystemConfig:
    # API_ID = os.getenv("TELEGRAM_API_ID") для тг
    # API_HASH = os.getenv("TELEGRAM_API_HASH") для тг
    TELEGRAM_CLIENT_APP_VERSION = "4.16.8-telethon"
    TELEGRAM_CLIENT_DEVICE_MODEL = "PC"
    TELEGRAM_CLIENT_SYSTEM_VERSION = "Windows 10"
    TELEGRAM_CLIENT_LANG_CODE = "ru"
    TELEGRAM_CLIENT_SYSTEM_LANG_CODE = "ru"


# Типы чатов Telegram
CHAT_TYPE_CHANNEL = "channel"
CHAT_TYPE_CHAT = "chat"
CHAT_TYPE_USER = "user"


# Ключи для данных сообщений
class MessageKeys:
    MESSAGE_ID = "message_id"
    USER_ID = "user_id"
    REPLY_TO = "reply_to_message_id"
    TEXT = "message_text"
    AUTHOR = "author_name"
    DATE = "date"
    REACTIONS = "reactions"
    MENTIONS = "mentions"


#  Форматы и шаблоны
JSON_INDENT = 4


class Extensions:
    JSON_EXTENSION = ".json"
    CHAT_FILE_EXTENSION = JSON_EXTENSION
    PDF_FILE_EXTENSION = ".pdf"
    HTML_FILE_EXTENSION = ".html"


class DateFormat:
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
    TIME_FORMAT = "%H-%M-%S"


# 🔗 URL шаблоны
TELEGRAM_URLS = {
    "USERNAME": "https://t.me/",
    "CHAT_ID": "https://t.me/c/",
    "CHANNEL": "https://t.me/+/",
}


class FileTemplates:
    """Шаблоны для имен файлов и директорий"""

    # Базовые имена
    METRICS_BASE_NAME = "metrics_"
    GRAPH_BASE_NAME = "graph_visualization_"
    REPORT_BASE_NAME = "report_"

    UNLOAD_OF_CHATS_BASE_NAME_LOG = "unload.log"
    ANALYZE_CHAT_BASE_NAME_LOG = "analysis.log"
    ANALYZE_CHAT_BASE_NAME = "analysis"

    # Шаблоны имен файлов
    CHAT_FILENAME = (
        "id={chat_id},social_account={social_account}, unload_date={date}{extension}"
    )

    PDF_REPORT_FILENAME = "{base_name}_{additional_name}, chat_name={chat_name}, phone_number={phone_number}, report_date={report_date}{extension}"

    METRICS_FILENAME = "{base_name}_{additional_name}, metrics_date={date}{extension}"

    GRAPH_VISUALIZATION = (
        "{base_name}_{additional_name}, graph_date={graph_date}{extension}"
    )

    # Шаблоны путей
    SESSION_PATH = "{storage_path}/session_{phone_number}"
    USER_DIR_PATH = "{base_path}/{user_name}"
    CHAT_DIR_PATH = "{user_path}/{chat_name}"
    FULL_NAME_TEMPLATE = "{first_name} {last_name}"


# 🔤 Текстовые шаблоны для форматирования графа
class TemplateStrings:
    USER_NODE_TITLE = "ID: {user_id}, Имя: {username}"
    MESSAGE_NODE_TITLE = "message_id: {message_id}"
    OPEN_GRAPH_LINK_TEXT = "Открыть интерактивный граф"


# ❓ Ключевые слова для анализа
QUESTION_KEYWORDS = [
    "кто",
    "что",
    "где",
    "когда",
    "почему",
    "как",
    "зачем",
    "сколько",
    "какой",
    "какая",
    "какое",
    "какие",
    "?",
    "ли",
]

# 🔍 Регулярные выражения
MENTION_REGEX = r"@(\w+)"
REACTION_REGEX = r"(\u2764|\ud83d\ude0d|\ud83d\ude0e|\ud83d\ude0a)"
URL_REGEX = r"https?://[^\s]+"


# 📋 Сообщения для логов
class LogMessages:
    # Информационные
    HELP_TELEGRAM_DESCRIPTION_UNLOADING_DATA = "Выгрузка данных из Telegram чата"
    HELP_TELEGRAM_USER_SYSTEM_NAME = "Имя пользователя системы"
    HELP_TELEGRAM_API_HASH = "API_HASH"
    HELP_TELEGRAM_API_ID = "API_ID"
    HELP_TELEGRAM_SOCIAL_ACCOUNT_NAME = "Название соц.сети"
    HELP_TELEGRAM_CHAT_NAME = "Название чата для выгрузки"
    HELP_TELEGRAM_PHONE = "Номер телефона для авторизации"
    HELP_TELEGRAM_OUTPUT = "Директория для сохранения данных(если не указана, используется по умолчанию путь формата: storage/<user>/<social>/<phone>/<chat>/<YYYY-MM-DD>/... .json"

    INFO_CONNECT_SUCCESS = "Подключение успешно."
    INFO_DATA_START = "Начинаем выгрузку данных из чата: {chat_name}"
    INFO_DATA_SAVED = "Данные сохранены в файл: {file_path}"
    INFO_DATA_LOADED = "Данные успешно загружены."
    INFO_MESSAGES_COLLECTED = "Собрано {count} сообщений."
    INFO_CHAT_FOUND = "Найден чат: {chat_name} (ID: {chat_id})"

    INFO_OBJECT_CHAT = (
        "Chat(ID='{chat_id}', Type='{chat_type}', Social='{social_account_name}')"
    )
    INFO_OBJECT_USER = "User(name='{self.name}', phones='{self.phone_numbers}')"

    # Предупреждения
    WARNING_EMPTY_DATA = "Загруженные данные пусты, анализ невозможен."
    WARNING_CHAT_NOT_FOUND = (
        "Чат '{chat_name}' не найден. Доступные чаты: {available_chats}"
    )
    WARNING_NO_REACTIONS = "В сообщении {message_id} не найдено реакций."
    WARNING_NOT_ACCESS_SOCIAL_NETWORK = "Не доступная социальная сеть"

    # ОШИБКИ
    ERROR_DATA_UNLOADING = "Ошибка при выгрузке данных"
    ERROR_CHAT_NOT_FOUND = (
        "Ошибка: Не удалось найти чат '{chat_url}'. Проверьте URL или username. {e}"
    )
    ERROR_UNEXPECTED = "Произошла непредвиденная ошибка: {e}"
    ERROR_CONNECTION = "Ошибка подключения к {social_network}: {e}"

    ERROR_TYPE_MISMATCH = (
        "Объект должен быть типа {expected_type}, получен {actual_type}"
    )
    ERROR_NONE_OBJECT = "Объект не может быть None"
    ERROR_NONE_PARAM = "Параметр '{param_name}' не может быть None"
    ERROR_EMPTY_STRING = "Строка не может быть пустой"
    ERROR_EMPTY_STRING_PARAM = "Параметр '{param_name}' не может быть пустой строкой"
    ERROR_EMPTY_COLLECTION = "Коллекция не может быть пустой"
    ERROR_EMPTY_COLLECTION_PARAM = (
        "Параметр '{param_name}' не может быть пустой коллекцией"
    )

    ERROR_FUNCTION_EXECUTION = "Ошибка в функции {function_name}: {error}"
    ERROR_ENTITY_FETCH_FAILED = "Не удалось получить entity для {chat_id}"

    ERROR_NETWORK_SOCIAL = "Неподдерживаемая соцсеть: {social_account_name}"
    ERROR_VALIDATION_ARGUMENTS = "Ошибка валидации аргументов: {error}"
    # Ошибки графа
    ERROR_USER_NOT_FOUND = "Пользователь не найден: {user_id}"
    ERROR_USERS_NOT_FOUND = (
        "Пользователи не найдены: from_user={from_user_id}, to_user={to_user_id}"
    )

    # для FileManager
    INFO_BASE_DIRECTORY_CREATED = (
        "Базовая директория FileManager создана: {directory_path}"
    )
    INFO_DIRECTORY_CREATED = "Создана директория: {directory_path}"
    INFO_CHAT_STORAGE_PATH = "Путь хранения чата: {storage_path}"
    INFO_CHAT_DATA_SAVED = "Данные чата сохранены в: {file_path}"
    WARNING_FILE_NOT_FOUND = "Файл не найден: {file_path}"
    INFO_DATA_LOADED_SUCCESS = "Успешно загружено {count} записей из {file_path}"
    ERROR_JSON_DECODE = "Ошибка декодирования JSON в файле {file_path}: {error}"
    ERROR_FILE_READING = "Ошибка чтения файла {file_path}: {error}"
    ERROR_CHAT_DATA_SAVING = (
        "Ошибка при сохранении данных для чата '{chat_name}': {error}"
    )

    # FileManager Сохранение отчета
    PDF_REPORT_TITLE = "Отчет по чату: {chat_name}"
    INFO_PDF_REPORT_SAVED = "Отчет успешно сохранен в: {file_path}"
    ERROR_PDF_REPORT_CREATION = "Не удалось создать PDF отчет"

    #  ДЛя ГРафа FileManager
    INFO_GRAPH_SAVED = "Интерактивный граф сохранён в {file_path}. Откройте файл в браузере для просмотра"

    # Сохранение метрик (используется FileManager)
    INFO_METRICS_SAVED = "Метрики анализа сохранены в файл: {file_path}"
    ERROR_METRICS_SAVING = "Ошибка при сохранении метрик в {directory_path}: {error}"

    # analysis_chat.py
    ERROR_ANALYSIS_NO_DATA = "Нет выгрузок до указанной даты."
    ERROR_ANALYSIS_WRONG_DATE_FORMAT = (
        "Неверный формат даты: {date}. Ожидается YYYY-MM-DD"
    )
    ERROR_FOUND_CHAT_UNLOADING_CHAT = "Файл не найден: {file_info}"

    # Для analysis_chat.py Анализ
    INFO_ANALYSIS_START = "Начинаем анализ данных из файла: {data_file}"
    ERROR_DATA_LOADING = "Не удалось загрузить данные для анализа"
    INFO_MESSAGES_LOADED = "Загружено {count} сообщений для анализа"
    INFO_ANALYSIS_RESULTS_SAVED = "Результаты анализа сохранены в: {file_path}"

    # CLI помощь для analysis_chat.py (добавлено для совместимости)
    HELP_ANALYSIS_DESCRIPTION = "Анализ данных чата из JSON файла"
    HELP_ANALYSIS_FILE = "Путь к файлу с данными чата (JSON)"
    HELP_ANALYSIS_OUTPUT = "Директория (обычно папка чата) для сохранения результатов"
    HELP_ANALYSIS_DATE = (
        "Фильтр по дате выгрузки (YYYY-MM-DD). Берём последнюю на/до даты"
    )

    # Тексты CLI вывода
    ANALYSIS_CLI_HEADER = "РЕЗУЛЬТАТЫ АНАЛИЗА ЧАТА"
    INFO_ANALYSIS_DIR = "Директория с результатами: {path}"
    INFO_METRICS_FILE_PATH = "Файл с метриками: {file_path}"
    INFO_LEGACY_FILE_PATH = "Файл с legacy результатами: {file_path}"
    INFO_VISUALIZATION_FILE_PATH = "Визуализация графа: {file_path}"
    INFO_SUMMARY_METRICS = "Ключевые метрики:"
    INFO_SUMMARY_USERS = "Всего пользователей: {value}"
    INFO_SUMMARY_INTERACTIONS = "Всего взаимодействий: {value}"
    INFO_SUMMARY_MESSAGES = "Всего сообщений: {value}"
    INFO_TOP_ACTIVE_HEADER = "Топ-3 самых активных пользователей:"
    INFO_TOP_ACTIVE_LINE = "  - {username}: {value} сообщений"
    INFO_METRICS_HEADER = "Ключевые метрики:"


class PythonSettings:
    """Настройки для Python-специфичных операций"""

    # Режимы работы с файлами
    FILE_READ_MODE = "r"
    FILE_WRITE_MODE = "w"
    FILE_APPEND_MODE = "a"
    FILE_BINARY_READ_MODE = "rb"
    FILE_BINARY_WRITE_MODE = "wb"

    # Кодировки
    ENCODING_UTF8 = "utf-8"
    ENCODING_CP1251 = "cp1251"

    # JSON настройки
    JSON_ENSURE_ASCII = False
    JSON_DEFAULT_INDENT = 4

    # Прочие настройки
    DEFAULT_BUFFER_SIZE = 8192
    DEFAULT_CHUNK_SIZE = 4096


# 🎯 Настройки анализа
ANALYSIS_SETTINGS = {
    "top_users_limit": 10,
    "graph_visualization": True,
    "save_metrics": True,
    "generate_pdf_report": False,
}


# 📊 Настройки визуализации графа
class GraphVisualizationSettings:
    """Настройки для визуализации графа"""

    # Настройки сети
    NETWORK_HEIGHT = "800px"
    NETWORK_WIDTH = "100%"
    NETWORK_BGCOLOR = "#222222"
    NETWORK_FONT_COLOR = "white"
    NETWORK_DIRECTED = True
    NETWORK_NOTEBOOK = False

    # Цвета узлов
    ANONYMOUS_USER_COLOR = "#FF6B6B"
    REGULAR_USER_COLOR = "#4ECDC4"
    DEFAULT_NODE_COLOR = "#7F7F7F"

    # Формы узлов
    ANONYMOUS_USER_SHAPE = "box"
    REGULAR_USER_SHAPE = "dot"

    # Размеры
    NODE_SIZE = 25
    EDGE_WIDTH = 2

    # Цвета ребер по типам
    MESSAGE_COLOR = "#1F77B4"
    REPLY_COLOR = "#FF7F0E"
    MENTION_COLOR = "#2CA02C"
    REACTION_COLOR = "#9467BD"

    # Прочие настройки
    DEFAULT_FILENAME = "chat_graph.html"
    BROWSER_URL_PREFIX = "file://"
    ARROWS_DIRECTION = "to"
    TITLE_NODES = "ID: {user_id}, name: {knot_name}"
    # Дополнительные обработчики ошибок внутри классов и функций и предупреждения о них:

    HELP_TELEGRAM_PHONE = "Номер телефона для авторизации"
    HELP_TELEGRAM_OUTPUT = "Директория для сохранения данных"
    INFO_CONNECT_SUCCESS = "Подключение успешно."
    INFO_DATA_START = "Начинаем выгрузку данных из чата: {chat_name}"
    INFO_DATA_SAVED = "Данные сохранены в файл: {file_path}"
    INFO_DATA_LOADED = "Данные успешно загружены."
    INFO_MESSAGES_COLLECTED = "Собрано {count} сообщений."
    INFO_CHAT_FOUND = "Найден чат: {chat_name} (ID: {chat_id})"
    INFO_OBJECT_CHAT = (
        "Chat(ID='{chat_id}', Type='{chat_type}', Social='{social_account_name}')"
    )
    INFO_OBJECT_USER = "User(name='{self.name}', phones='{self.phone_numbers}')"

    # Предупреждения
    WARNING_EMPTY_DATA = "Загруженные данные пусты, анализ невозможен."
    WARNING_CHAT_NOT_FOUND = (
        "Чат '{chat_name}' не найден. Доступные чаты: {available_chats}"
    )
    WARNING_NO_REACTIONS = "В сообщении {message_id} не найдено реакций."
    WARNING_NOT_ACCESS_SOCIAL_NETWORK = "Не доступная социальная сеть"

    # Ошибки
    ERROR_DATA_UNLOADING = "Ошибка при выгрузке данных"
    ERROR_CHAT_NOT_FOUND = (
        "Ошибка: Не удалось найти чат '{chat_url}'. Проверьте URL или username. {e}"
    )
    ERROR_UNEXPECTED = "Произошла непредвиденная ошибка: {e}"
    ERROR_TYPE_MISMATCH = (
        "Объект должен быть типа {expected_type}, получен {actual_type}"
    )
    ERROR_NONE_OBJECT = "Объект не может быть None"
    ERROR_NONE_PARAM = "Параметр '{param_name}' не может быть None"
    ERROR_EMPTY_STRING = "Строка не может быть пустой"
    ERROR_EMPTY_STRING_PARAM = "Параметр '{param_name}' не может быть пустой строкой"
    ERROR_EMPTY_COLLECTION = "Коллекция не может быть пустой"
    ERROR_EMPTY_COLLECTION_PARAM = (
        "Параметр '{param_name}' не может быть пустой коллекцией"
    )
    ERROR_FUNCTION_EXECUTION = "Ошибка в функции {function_name}: {error}"

    # Ошибки графа
    ERROR_USER_NOT_FOUND = "Пользователь не найден: {user_id}"
    ERROR_USERS_NOT_FOUND = (
        "Пользователи не найдены: from_user={from_user_id}, to_user={to_user_id}"
    )

    # для FileManager
    INFO_BASE_DIRECTORY_CREATED = (
        "Базовая директория FileManager создана: {directory_path}"
    )
    INFO_DIRECTORY_CREATED = "Создана директория: {directory_path}"
    INFO_CHAT_STORAGE_PATH = "Путь хранения чата: {storage_path}"
    INFO_CHAT_DATA_SAVED = "Данные чата сохранены в: {file_path}"
    WARNING_FILE_NOT_FOUND = "Файл не найден: {file_path}"
    INFO_DATA_LOADED_SUCCESS = "Успешно загружено {count} записей из {file_path}"
    ERROR_JSON_DECODE = "Ошибка декодирования JSON в файле {file_path}: {error}"
    ERROR_FILE_READING = "Ошибка чтения файла {file_path}: {error}"
    ERROR_CHAT_DATA_SAVING = (
        "Ошибка при сохранении данных для чата '{chat_name}': {error}"
    )

    # FileManager Сохранение отчета
    PDF_REPORT_TITLE = "Отчет по чату: {chat_name}"
    INFO_PDF_REPORT_SAVED = "Отчет успешно сохранен в: {file_path}"
    ERROR_PDF_REPORT_CREATION = "Ошибка при создании PDF-отчета: {error}"

    # Для analysis_chat.py
    INFO_ANALYSIS_START = "Начинаем анализ данных из файла: {data_file}"
    ERROR_DATA_LOADING = "Не удалось загрузить данные для анализа"
    INFO_MESSAGES_LOADED = "Загружено {count} сообщений для анализа"
    INFO_ANALYSIS_RESULTS_SAVED = "Результаты анализа сохранены в: {file_path}"


class PythonSettings:
    """Настройки для Python-специфичных операций"""

    # Режимы работы с файлами
    FILE_READ_MODE = "r"
    FILE_WRITE_MODE = "w"
    FILE_APPEND_MODE = "a"
    FILE_BINARY_READ_MODE = "rb"
    FILE_BINARY_WRITE_MODE = "wb"

    # Кодировки
    ENCODING_UTF8 = "utf-8"
    ENCODING_CP1251 = "cp1251"

    # JSON настройки
    JSON_ENSURE_ASCII = False
    JSON_DEFAULT_INDENT = 4

    # Прочие настройки
    DEFAULT_BUFFER_SIZE = 8192
    DEFAULT_CHUNK_SIZE = 4096


# 📊 Настройки визуализации графа
class GraphVisualizationSettings:
    """Настройки для визуализации графа"""

    # Настройки сети
    NETWORK_HEIGHT = "800px"
    NETWORK_WIDTH = "100%"
    NETWORK_BGCOLOR = "#222222"
    NETWORK_FONT_COLOR = "white"
    NETWORK_DIRECTED = True
    NETWORK_NOTEBOOK = False

    # Цвета узлов
    ANONYMOUS_USER_COLOR = "#FF6B6B"
    REGULAR_USER_COLOR = "#4ECDC4"
    DEFAULT_NODE_COLOR = "#7F7F7F"

    # Формы узлов
    ANONYMOUS_USER_SHAPE = "box"
    REGULAR_USER_SHAPE = "dot"

    # Размеры
    NODE_SIZE = 25
    EDGE_WIDTH = 2

    # Цвета ребер по типам
    MESSAGE_COLOR = "#1F77B4"
    REPLY_COLOR = "#FF7F0E"
    MENTION_COLOR = "#2CA02C"
    REACTION_COLOR = "#9467BD"

    # Прочие настройки
    DEFAULT_FILENAME = "chat_graph.html"
    BROWSER_URL_PREFIX = "file://"
    ARROWS_DIRECTION = "to"


# Дополнительные обработчики ошибок внутри классов и функций и предупреждения о них:
