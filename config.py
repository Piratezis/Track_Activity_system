# """Задачи на файл.
# 1) Принты на логи +
# 2) Вынести переменные +
# 3) Проверка на все исключения
# 4) Интеграция логики узлов
# 5) СТандарты +
# """
#
# 1 📜 Конфигурация - общее поведение системы

TELEGRAM_KEY = "telegram"
SLACK_KEY = "slack"  # Исправлено на SLACK_KEY

SOCIAL_NETWORK_DICT = {TELEGRAM_KEY: "Telegram", SLACK_KEY: "slack"}


STORAGE_DIR = "storage"  # Каталог для хранения данных
DEFAULT_USERNAME = "Илья Волков"  # Имя пользователя по умолчанию
UNKNOWN_AUTHOR = "Неизвестный"  # Сообщение для неизвестного автора

# Настройки Telegram
# Telegram API
CHAT_NAME = "Восхождение по низу🧿"
PHONE_NUMBERS = ["+79935474292"]  # для авторизации в Telegram
CHAT_TYPE_CHANNEL_TEXT_TELETHON = "channel"
CHAT_TYPE_CHAT_TEXT_TELETHON = "chat"
USERNAME_TEXT_TELETHON = "username"
API_ID = "25290973"  # изменяемые
API_HASH = "35b85b1a818c842836e7f5fb0bdcadb7"  # изменяемые


MESSAGE_ID_KEY = "message_id"
USER_ID_KEY = "user_id"
REPLY_TO_ID_KEY = "reply_to_message_id"
MESSAGE_TEXT_KEY = "message_text"  # Добавлено для ChatAnalyzer
AUTHOR_NAME_KEY = "author_name"  # Добавлено для ChatAnalyzer и TelegramChat
DATE_KEY = "date"  # Добавлено для TelegramChat
REACTIONS_KEY = "reactions"
MENTIONS_KEY = "mentions"

SESSION_NAME_TEMPLATE = "{phone_number}_session"  # Шаблон для имени сессии
TELEGRAM_CLIENT_APP_VERSION = "4.16.8-telethon"  # Версия клиента
TELEGRAM_CLIENT_DEVICE_MODEL = "PC"  # Модель устройства (универсальное)
TELEGRAM_CLIENT_SYSTEM_VERSION = "Windows 10"  # Версия системы
TELEGRAM_CLIENT_LANG_CODE = "ru"  # Код языка (изменен на русский)
TELEGRAM_CLIENT_SYSTEM_LANG_CODE = "ru"  # Код системного языка (изменен на русский)
TELEGRAM_TITLE_ATTRIBUTE = "title"  # Название атрибута для получения имени канала


CHAT_URLS = ["https://t.me/you_biohackages"]  # URL или имя чата для анализа


# 4 ! Предупреждения и ошибки

# Текст ошибки при поиске чата
CHAT_NOT_FOUND_ERROR = (
    "Ошибка: Не удалось найти чат '{chat_url}'. Проверьте URL или username. {e}"
)

# Текст для непредвиденных ошибок
UNEXPECTED_ERROR = "Произошла непредвиденная ошибка: {e}"
OLD_METHOD_WARNING = "Это предупреждение, метод устарел"
WARNING_EMPTY_DATA = "Загруженные данные пусты, анализ невозможен."

# 5 🕰️ Настройки времени и лимитов


LOG_ROTATION_SIZE = 500 * 1024 * 1024  # Размер файла логов в байтах (500 МБ)

# 6 ℹ️ Информационные сообщения для логов

INFO_INIT_APP = "Инициализация App для чата: {chat_url}"
INFO_CONNECT_ATTEMPT = "Попытка подключения к Telegram..."
INFO_CONNECT_SUCCESS = "Подключение успешно."
INFO_CHAT_NOT_FOUND = "Чат '{chat_url}' не найден в списке, добавляем..."
INFO_START_COLLECTION = "Сбор и анализ сообщений из чата: {chat_url}"
INFO_MESSAGES_COLLECTED = "Собрано {count} сообщений."
INFO_SAVE_DATA = "Данные сохранены в файл: {file_path}"
INFO_LOAD_DATA = "Данные успешно загружены."
INFO_START_ANALYSIS = "Начинаем анализ чата '{chat_url}'."
INFO_ANALYSIS_REPLIES_DONE = "Анализ ответов завершен."
INFO_MOST_ACTIVE_FOUND = "Найдены самые активные участники."
INFO_ANALYSIS_QUESTIONS_DONE = "Анализ вопросов завершен."
INFO_MOST_ACTIVE_REPLIER = "Кто чаще всех отвечал: {name}"
INFO_MOST_REPLIED_TO = "Кто чаще всех получал ответы: {name}"
INFO_QUESTIONS_COUNT = "Количество вопросов от каждого пользователя: {questions}"
# Графы
INFO_GRAPH_BUILD_START = "Начинаем построение графа сообщений и пользователей..."
INFO_GRAPH_BUILD_DONE = (
    "Построение графа завершено. Узлов: {knots_count}, Рёбер: {edges_count}."
)
WARNING_NO_USERS_IN_CHAT = "В чате не найдено пользователей. Анализ связей невозможен."
WARNING_NO_REACTIONS = "В сообщении {message_id} не найдено реакций."
WARNING_NO_MENTIONS = "В сообщении {message_id} не найдено упоминаний."
#
# # 7 🚀 Вспомогательные сообщения и константы
#
# TELEGRAM_ACCOUNT_NAME = "TelegramAccount"  # Имя класса для путей
PRINT_CONNECT_MESSAGE = "Конект в телеге"  # Вывод в консоль
PRINT_CHAT_ADDED = "чат добавлен"  # Вывод в консоль
JSON_INDENT = 4  # Отступ в JSON-файле
JSON_ENCODING = "utf-8"  # Кодировка JSON-файлов
CHAT_FILE_EXTENSION = ".json"  # Расширение для файлов чатов
HTTPS_LINK_TEXT_CHAT_USERNAME = "https://t.me/" # Базовый URL Telegram
HTTPS_LINK_TEXT_CHAT_ID = "https://t.me/c/"
QUESTION_KEYWORDS = [
    "кто",
    "что",
    "где",
    "когда",
    "почему",
    "как",
]  # Ключевые слова для определения вопросов
FULL_NAME_TEMPLATE = "{first_name} {last_name}"  # Шаблон для полного имени пользователя
# Регулярные выражения для поиска инфы в сообщениях
MENTION_REGEX = r"@(\w+)"  # Регулярное выражение для поиска упоминаний
REACTION_REGEX = (
    r"(\u2764|\ud83d\ude0d|\ud83d\ude0e|\ud83d\ude0a)"  # Примерный список смайликов
)
