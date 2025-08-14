# """Задачи на файл.
# 1) Принты на логи
# 2) Вынести переменные
# 3) Проверка на все исключения
# 4) Интеграция логики узлов
# 5) СТандарты
# """
#
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from loguru import logger
from config import JSON_INDENT, JSON_ENCODING, QUESTION_KEYWORDS
from enums import KnotType, EdgeType, MessageKeys
from models import TelegramChat, Knot, Edge


#
#
# # _____________________________________________________________________________
class FileManager:
    """
    Класс для управления файлами: сохранения и загрузки данных.
    Работает с объектами pathlib.Path для удобства и надежности.
    """

    def __init__(self,
                 base_storage_dir: Path):  # Ожидает Path для корневой директории
        self.base_storage_dir = base_storage_dir
        self.base_storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            f"Базовая директория FileManager создана: {self.base_storage_dir}")

    def create_object_dir(self, obj_dir_name: str, parent_dir: Path):
        """
        Создает директорию для объекта внутри указанной родительской директории.

        Args:
            obj_dir_name (str): Имя папки.
            parent_dir (pathlib.Path): Родительская директория, где будет создана папка.

        Returns:
            pathlib.Path: Полный путь к созданной директории.
        """
        new_dir_path = parent_dir / obj_dir_name
        new_dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Создана директория: {new_dir_path}")
        return new_dir_path

    def save_chat_json(self, chat: TelegramChat,
                       data: List[Dict[str, Any]]) -> None:
        """
        Сохраняет данные чата в JSON-файл напрямую в папке аккаунта.

        :param chat: Объект TelegramChat.
        :param data: Данные для сохранения (список словарей).
        """
        # Создаём имя файла, используя ID чата
        file_name = f"{chat.chat_id}.json"

        # Формируем полный путь к файлу в папке аккаунта
        file_path = chat.storage_path / file_name
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        except IOError as e:
            print(f"Ошибка при сохранении данных для чата '{chat.name}': {e}")
        return file_path

    def load_chat_json(self, file_path: Path) -> List[Dict[str, Any]] | None:
        """
        Загружает данные из JSON-файла.

        :param file_path: Путь к файлу.
        :return: Данные в формате Python (список словарей) или None, если файл не найден.
        """
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding=JSON_ENCODING) as f:
            data = json.load(f)
        return data


# # _____________________________________________________________________________
class ChatAnalyzer:
    """
    Класс для анализа данных чата.
    """

    def analyze_replies(
            self, data: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, int], Dict[str, int]]:
        """
        Анализирует, кто кому отвечал в чате.

        :param chat_data: Список сообщений (словарей) из чата.
        :return: Два словаря: replies_from (кто отвечал) и replies_to (кому отвечали).
        """
        replies_from: Dict[str, int] = {}
        replies_to: Dict[str, int] = {}

        # ИСПРАВЛЕНИЕ: Добавлены .value к членам MessageKeys
        message_map = {
            msg[MessageKeys.MESSAGE_ID]: msg[MessageKeys.USER_ID] for msg in
            data
        }

        for message in data:
            author_id = message.get(MessageKeys.USER_ID)
            reply_to_id = message.get(MessageKeys.REPLY_TO_ID)

            if author_id and reply_to_id:
                if author_id not in replies_from:
                    replies_from[author_id] = 0
                replies_from[author_id] += 1

                original_author_id = message_map.get(reply_to_id)
                if original_author_id:
                    if original_author_id not in replies_to:
                        replies_to[original_author_id] = 0
                    replies_to[original_author_id] += 1
        return replies_from, replies_to

    def get_most_active_repliers(
            self, replies_from: Dict[str, int], replies_to: Dict[str, int]
    ) -> Tuple[Any, Any]:
        """
        Определяет самого активного отвечающего и того, кому чаще всего отвечали.
        """
        try:
            most_replied = max(replies_to, key=replies_to.get)
        except ValueError:
            most_replied = None

        try:
            most_active_replier = max(replies_from, key=replies_from.get)
        except ValueError:
            most_active_replier = None

        return most_active_replier, most_replied

    def analyze_questions(self, chat_data: List[Dict[str, Any]]) -> Dict[
        str, int]:
        """
        Подсчитывает количество вопросов от каждого пользователя.
        """
        questions_by_user: Dict[str, int] = {}

        # Используем константы для ключей, чтобы избежать ошибок с Enum
        MESSAGE_TEXT_KEY = MessageKeys.MESSAGE_TEXT.value
        USER_ID_KEY = MessageKeys.USER_ID.value

        for message in chat_data:
            text = message.get(MESSAGE_TEXT_KEY, "").lower()
            user_id = message.get(USER_ID_KEY)

            is_question = any(
                keyword in text for keyword in QUESTION_KEYWORDS
            ) or text.endswith("?")

            if is_question and user_id:
                if user_id not in questions_by_user:
                    questions_by_user[user_id] = 0
                questions_by_user[user_id] += 1
        return questions_by_user


# _____________________________________________________________________________

class GraphCreator:
    """
    Класс для построения графа из сообщений и пользователей чата.
    Создает узлы (пользователи, сообщения) и ребра (связи).
    """

    # Определяем константы для ключей, чтобы избежать ошибок с Enum
    USER_ID_KEY = MessageKeys.USER_ID.value
    AUTHOR_NAME_KEY = MessageKeys.AUTHOR_NAME.value
    MESSAGE_ID_KEY = MessageKeys.MESSAGE_ID.value
    REPLY_TO_ID_KEY = MessageKeys.REPLY_TO_ID.value
    MESSAGE_TEXT_KEY = MessageKeys.MESSAGE_TEXT.value

    def __init__(self, messages: List[Dict[str, Any]],
                 users: List[Dict[str, Any]]):
        self.messages = messages
        self.users = users
        self.knots = {}
        self.edges = {}
        self.edge_id_counter = 0

    def _create_user_knots(self):
        """Создает узлы для всех пользователей чата."""
        for user_data in self.users:
            user_id = user_data.get(self.USER_ID_KEY)
            user_name = user_data.get(self.AUTHOR_NAME_KEY)
            if user_id is not None and user_name is not None:
                knot = Knot(user_id, KnotType.USER, {"name": user_name})
                self.knots[user_id] = knot

    def _create_message_knots(self):
        """Создает узлы для всех сообщений."""
        for message_data in self.messages:
            message_id = message_data.get(self.MESSAGE_ID_KEY)
            message_text = message_data.get(self.MESSAGE_TEXT_KEY, '')
            if message_id is not None:
                knot = Knot(message_id, KnotType.MESSAGE,
                            {"text": message_text})
                self.knots[message_id] = knot

    def _create_edge(self, sender: Knot, receiver: Knot, edge_type: EdgeType,
                     content: str = None):
        """Создает новое ребро и добавляет его в списки узлов."""
        self.edge_id_counter += 1
        edge = Edge(self.edge_id_counter, sender, receiver, edge_type, content)
        self.edges[self.edge_id_counter] = edge
        sender.add_edge(edge, is_outgoing=True)
        receiver.add_edge(edge, is_outgoing=False)

    def create_graph(self) -> Tuple[Dict[int, Knot], Dict[int, Edge]]:
        """
        Основной метод для построения графа.
        """
        self._create_user_knots()
        self._create_message_knots()

        for message_data in self.messages:
            sender_id = message_data.get(self.USER_ID_KEY)
            message_id = message_data.get(self.MESSAGE_ID_KEY)
            reply_to_id = message_data.get(self.REPLY_TO_ID_KEY)

            if sender_id in self.knots and message_id in self.knots:
                sender_knot = self.knots[sender_id]
                message_knot = self.knots[message_id]

                self._create_edge(sender_knot, message_knot, EdgeType.SENT,
                                  None)

                if reply_to_id and reply_to_id in self.knots:
                    receiver_knot = self.knots[reply_to_id]
                    self._create_edge(message_knot, receiver_knot,
                                      EdgeType.REPLY_TO, None)

        return self.knots, self.edges
