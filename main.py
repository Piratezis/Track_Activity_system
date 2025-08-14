"""Задачи на файл.
1) Принты на логи +
2) Вынести переменные +
3) Проверка на все исключения -
4) Интеграция логики узлов
5) СТандарты +

"""

from enums import MessageKeys, KnotType, EdgeType
import asyncio
from pathlib import Path
from models import User, TelegramAccount, TelegramChat
from manager import FileManager, ChatAnalyzer
from loguru import logger
from config import (
    API_ID,
    API_HASH,
    PHONE_NUMBERS,
    CHAT_NAME,
    STORAGE_DIR,
    DEFAULT_USERNAME,
    UNKNOWN_AUTHOR,
    LOG_ROTATION_SIZE,
    CHAT_NOT_FOUND_ERROR,
    UNEXPECTED_ERROR,
    INFO_INIT_APP,
    INFO_CONNECT_ATTEMPT,
    INFO_CONNECT_SUCCESS,
    INFO_CHAT_NOT_FOUND,
    INFO_START_COLLECTION,
    INFO_MESSAGES_COLLECTED,
    INFO_SAVE_DATA,
    INFO_LOAD_DATA,
    INFO_START_ANALYSIS,
    INFO_ANALYSIS_REPLIES_DONE,
    INFO_MOST_ACTIVE_FOUND,
    INFO_ANALYSIS_QUESTIONS_DONE,
    INFO_MOST_ACTIVE_REPLIER,
    INFO_MOST_REPLIED_TO,
    INFO_QUESTIONS_COUNT,
    WARNING_EMPTY_DATA,
    CHAT_URLS,
)
from manager import FileManager, ChatAnalyzer, GraphCreator

# 1) стандарты оформления кода почитать
# Тест для проверки кода(посмотреть, pytest)
# 2) проверка на все исключения
# 3) вынести переменные все + Enum

# 4) кто на чьи сообщения ответил, и кто на чьи чаще отвечает - посчитать
# 5) Вершины (юзер, сообщение), ребро - (написал, ответил)

# 6) networkx и другие и библиотека для визуализации, характеристики графа- вывести пользователей без ребер, свойства графа, посчитать метрики

# A->B
# A - 0 - эту связь не учитываю
# logger.debug(): Очень детальная информация, полезная только для отладки.
#
# logger.info(): Общие информационные сообщения, например, "Приложение запущено".
#
# logger.warning(): Предупреждения, которые не блокируют работу, но на которые стоит обратить внимание.
#
# logger.error(): Сообщения об ошибках.
#
# logger.critical(): Критические ошибки, из-за которых приложение может завершить работу.
# ______________________________________________________________________

# Создаем файл file.log и ротируем его каждые 500 МБ
logger.add("file.log", rotation=LOG_ROTATION_SIZE)


# class App:
#     """
#     Класс для управления всем процессом анализа чата Telegram.
#
#     Инкапсулирует логику подключения, получения данных,
#     их сохранения и последующего анализа.
#     """
#
#     def __init__(self, api_id: str, api_hash: str, phone_number: str, chat_url: str):
#         # Инициализация всех атрибутов
#         self.user = None
#         self.telegram_chat = None
#         self.file_manager = FileManager()
#         self.chat_analyzer = ChatAnalyzer()
#
#         # Инициализация пользователя и аккаунта Telegram
#         storage_dir = pathlib.Path(STORAGE_DIR)
#         self.user = User(
#             name=DEFAULT_USERNAME, phone_number=phone_number, storage_dir=storage_dir
#         )
#         self.telegram_account = TelegramAccount(self.user, api_id, api_hash)
#
#         self.chat_url = chat_url
#         logger.info(INFO_INIT_APP.format(chat_url=self.chat_url))
#
#     async def run(self):
#         """
#         Запуск всего процесса.
#         """
#         try:
#             # 1. Подключение к аккаунту Telegram
#             logger.info(INFO_CONNECT_ATTEMPT)
#             await self.telegram_account.connect()
#             logger.info(INFO_CONNECT_SUCCESS)
#
#             # 2. Получение объекта чата
#             self.telegram_chat = self.telegram_account.chats.get(self.chat_url)
#             if not self.telegram_chat:
#                 logger.info(INFO_CHAT_NOT_FOUND.format(chat_url=self.chat_url))
#                 self.telegram_chat = await self.telegram_account.add_chat(self.chat_url)
#
#             logger.info(
#                 INFO_START_COLLECTION.format(chat_url=self.telegram_chat.chat_url)
#             )
#             messages = await self.telegram_chat.get_messages()
#             logger.info(INFO_MESSAGES_COLLECTED.format(count=len(messages)))
#
#             # 3. Сохранение и загрузка данных
#             self.file_manager.save(self.telegram_chat.storage_path, messages)
#             logger.info(
#                 INFO_SAVE_DATA.format(file_path=self.telegram_chat.storage_path)
#             )
#
#             saved_data = self.file_manager.load(self.telegram_chat.storage_path)
#             logger.info(INFO_LOAD_DATA)
#             # Создаем словарь-маппинг, где ключи - это строковые значения из Enum
#             MESSAGE_KEYS_MAP = {
#                 "message_id": "message_id",
#                 "user_id": "user_id",
#                 "reply_to_message_id": "reply_to_message_id",
#                 "message_text": "message_text",
#                 "author_name": "author_name",
#                 "date": "date"
#             }
#             if saved_data:
#                 # 4. Подготовка данных для анализа
#                 user_id_to_name_map = {
#                     msg[MESSAGE_KEYS_MAP["user_id"]]: msg[
#                         MESSAGE_KEYS_MAP["author_name"]]
#                     for msg in saved_data
#                     if msg.get(MESSAGE_KEYS_MAP["user_id"]) is not None
#                 }
#
#                 logger.info(
#                     INFO_START_ANALYSIS.format(chat_url=self.telegram_chat.chat_url)
#                 )
#
#                 # 5. Анализ сообщений
#                 replies_from, replies_to = self.chat_analyzer.analyze_replies(
#                     saved_data
#                 )
#                 logger.debug(INFO_ANALYSIS_REPLIES_DONE)
#
#                 most_active_replier_id, most_replied_id = (
#                     self.chat_analyzer.get_most_active_repliers(
#                         replies_from, replies_to
#                     )
#                 )
#                 logger.debug(INFO_MOST_ACTIVE_FOUND)
#
#                 questions = self.chat_analyzer.analyze_questions(saved_data)
#                 logger.debug(INFO_ANALYSIS_QUESTIONS_DONE)
#
#                 most_active_replier_name = user_id_to_name_map.get(
#                     most_active_replier_id, UNKNOWN_AUTHOR
#                 )
#                 most_replied_name = user_id_to_name_map.get(
#                     most_replied_id, UNKNOWN_AUTHOR
#                 )
#
#                 logger.info(
#                     INFO_MOST_ACTIVE_REPLIER.format(name=most_active_replier_name)
#                 )
#                 logger.info(INFO_MOST_REPLIED_TO.format(name=most_replied_name))
#
#                 questions_by_name = {
#                     user_id_to_name_map.get(uid, UNKNOWN_AUTHOR): count
#                     for uid, count in questions.items()
#                 }
#                 logger.info(INFO_QUESTIONS_COUNT.format(questions=questions_by_name))
#             else:
#                 logger.warning(WARNING_EMPTY_DATA)
#                 # ______________________________________________________________________
#
#                 # Получаем список пользователей чата через класс TelegramChat
#                 chat_users_names = await self.telegram_chat.get_list_users()
#
#                 # Поскольку get_list_users возвращает только имена, а не словари с id,
#                 # нам нужно преобразовать данные.
#                 # Для упрощения примера создадим "заглушки" для user_id
#                 chat_users_data = []
#                 # Чтобы избежать ошибки, если `chat_users_names` пуст, используем enumerate
#                 for i, name in enumerate(chat_users_names, 1):
#                     chat_users_data.append(
#                         {MessageKeys.USER_ID: i, MessageKeys.AUTHOR_NAME: name}
#                     )
#
#                 # Создаём и строим граф связей
#                 graph_creator = GraphCreator(saved_data, chat_users_data)
#                 knots, edges = graph_creator.create_graph()
#
#                 # Выводим связи "пользователь -> отправил -> сообщение" и "сообщение -> ответило -> сообщение"
#                 for edge in edges.values():
#                     if edge.edge_type == EdgeType.SENT:
#                         sender_name = edge.sender.data.get("name", UNKNOWN_AUTHOR)
#                         message_text = edge.receiver.data.get("text", "Нет текста")
#                         logger.info(
#                             f"Узел: {sender_name} - Ребро: {edge.edge_type.value} - Узел: {message_text}"
#                         )
#
#                     elif edge.edge_type == EdgeType.REPLY_TO:
#                         sender_knot = edge.sender
#                         receiver_knot = edge.receiver
#
#                         # Находим отправителя сообщения, на которое был дан ответ
#                         reply_sender = "Неизвестный"
#                         # Ищем ребро SENT, ведущее к сообщению, на которое ответили
#                         for incoming_edge in receiver_knot.incoming_edges.values():
#                             if incoming_edge.edge_type == EdgeType.SENT:
#                                 reply_sender = incoming_edge.sender.data.get(
#                                     "name", UNKNOWN_AUTHOR
#                                 )
#                                 break
#
#                         message_text = sender_knot.data.get("text", "Нет текста")
#                         logger.info(
#                             f"Узел: {message_text} - Ребро: {edge.edge_type.value} - Узел: {reply_sender}"
#                         )
#             # ______________________________________________________________________
#         except ValueError as e:
#             logger.error(CHAT_NOT_FOUND_ERROR.format(chat_url=self.chat_url, e=e))
#         except Exception as e:
#             logger.critical(UNEXPECTED_ERROR.format(e=e))
class App:
    def __init__(self, user: User):
        self.user = user

        # Корневая директория для всех данных приложения
        # Она создается относительно текущей рабочей директории
        self.base_app_storage_root = Path.cwd() / STORAGE_DIR
        self.file_manager = FileManager(base_storage_dir=self.base_app_storage_root)
        self.chat_analyzer = ChatAnalyzer()


    async def run(self):  # Метод run теперь асинхронный
        logger.info("Запуск приложения...")

        # Создание папки для пользователя внутри базовой директории приложения
        user_dir_path = self.file_manager.create_object_dir(
            obj_dir_name=self.user.name,
            parent_dir=self.file_manager.base_storage_dir
        )
        self.user.storage_path = user_dir_path
        logger.info(f"Папка пользователя создана: {user_dir_path}")

        # Инициализация объекта соц. аккаунта
        selected_phone_number = self.user.phone_numbers[0]

        new_social_account = TelegramAccount(
            user=self.user,
            # Передаем данные пользователя и авторизации для создания аккаунта
            phone_number=selected_phone_number,
            api_id=API_ID,
            api_hash=API_HASH,
        )
        logger.info(
            f"Инициализирован TelegramAccount для {new_social_account.phone_number}"
        )

        # Асинхронное подключение к Telegram API
        try:
            await new_social_account.connect()
            logger.info(
                f"Подключение TelegramAccount успешно для {new_social_account.phone_number}"
            )
        except Exception as e:
            logger.error(f"Ошибка при подключении TelegramAccount: {e}")
            return  # Прерываем выполнение в случае ошибки

        # Добавляем соц. аккаунт к пользователю
        self.user.add_social_account(new_social_account)
        logger.info(
            f"Соц. аккаунт добавлен к пользователю. Всего аккаунтов: {len(self.user.social_accounts)}"
        )
        # Создаем директорию, если её нет
        new_social_account.storage_path.mkdir(
            parents=True, exist_ok=True
        )

        logger.info(
            f"Путь хранения соц. аккаунта: {new_social_account.storage_path}")

        # Создание объекта чата и добавление к соц. аккаунту
        # Получаем все чаты из Telegram (асинхронная операция)
        all_chats_in_social_account = await new_social_account.get_all_chats()

        # Находим ID нужного чата по его имени
        chat_name = CHAT_NAME
        chat_id = all_chats_in_social_account[chat_name]

        # Создаем объект чата
        chat1 = TelegramChat(
            chat_id=chat_id, name=chat_name, social_account=new_social_account
        )

        # Асинхронно инициализируем чат, чтобы получить 'entity'
        await chat1.initialize()

        # Создаем директорию для хранения данных чата
        chat1.storage_path = self.file_manager.create_object_dir(
            obj_dir_name=chat1.name, parent_dir=new_social_account.storage_path
        )

        # Добавляем чат к аккаунту
        await new_social_account.add_chat(chat1)

        data_chat1_new = await chat1.get_messages()
        chat1_file_path=self.file_manager.save_chat_json(chat=chat1, data=data_chat1_new)
        logger.info(INFO_SAVE_DATA)

        data_chat1_load = self.file_manager.load_chat_json(file_path=chat1_file_path)
        logger.info(INFO_LOAD_DATA)
        graph_creator = GraphCreator(data_chat1_load, await chat1.get_list_users())
        #replies_from, replies_to = chat_analyzer.analyze_replies(data=data_chat1_load)




        logger.info("Приложение завершило работу.")


# --- Блок запуска приложения ---
if __name__ == "__main__":
    user1 = User(name=DEFAULT_USERNAME, phone_numbers=PHONE_NUMBERS)

    app_instance = App(user=user1)  # Объект приложения для пользователя
    try:
        asyncio.run(app_instance.run())  # Запускаем асинхронный метод
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем.")
    except Exception as e:
        logger.exception("Произошла непредвиденная ошибка при запуске приложения.")
