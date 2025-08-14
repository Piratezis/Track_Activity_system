# """Задачи на файл.
# 1) Принты на логи +
# 2) Вынести переменные +
# 3) Проверка на все исключения
# 4) Интеграция логики узлов
# 5) СТандарты +
#
# """
#
import pathlib
from abc import ABC, abstractmethod
from telethon import TelegramClient
from telethon.tl.types import PeerChannel, Channel, User as TelethonUser
from loguru import logger
from config import (
    STORAGE_DIR,
    UNKNOWN_AUTHOR,
    SOCIAL_NETWORK_DICT,
    TELEGRAM_KEY,
    MESSAGE_ID_KEY,
    USER_ID_KEY,
    MESSAGE_TEXT_KEY,
    AUTHOR_NAME_KEY,
    DATE_KEY,
    REPLY_TO_ID_KEY,
    SESSION_NAME_TEMPLATE,
    TELEGRAM_CLIENT_APP_VERSION,
    TELEGRAM_CLIENT_DEVICE_MODEL,
    TELEGRAM_CLIENT_SYSTEM_VERSION,
    TELEGRAM_CLIENT_LANG_CODE,
    TELEGRAM_CLIENT_SYSTEM_LANG_CODE,
    PRINT_CONNECT_MESSAGE,
    PRINT_CHAT_ADDED,
    CHAT_FILE_EXTENSION,
    FULL_NAME_TEMPLATE,
    TELEGRAM_TITLE_ATTRIBUTE,
    CHAT_TYPE_CHANNEL_TEXT_TELETHON,
    USERNAME_TEXT_TELETHON,
    HTTPS_LINK_TEXT_CHAT_USERNAME,
    HTTPS_LINK_TEXT_CHAT_ID,
    CHAT_TYPE_CHAT_TEXT_TELETHON
)
from enums import KnotType, EdgeType


# # ______________________________________________________________________
class User:
    def __init__(self, name: str, phone_numbers: list):
        self.name = name
        self.phone_numbers = phone_numbers
        self.social_accounts = []
        self.storage_path = None

    def add_social_account(self, account):
        self.social_accounts.append(account)

    def get_social_accounts(self):
        return self.social_accounts

    def __str__(self):
        return f"User(name='{self.name}', phones='{self.phone_numbers}')"


class SocialAccount(ABC):
    def __init__(self, name: str, phone_number: str):
        self.name = name
        self.phone_number = phone_number
        self.session_path: pathlib.Path | None = None
        self.storage_path: pathlib.Path | None = None

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def get_chats(self):
        pass

    @abstractmethod
    async def add_chat(self, chat_url: str):
        pass


class Chat(ABC):
    """
    Абстрактный базовый класс для всех типов чатов социальных сетей.
    Содержит общие поля и абстрактные методы для взаимодействия с чатами.
    """

    def __init__(
            self,
            chat_id: int | str,
            # Уникальный ID чата (числовой или строковый)
            social_account: SocialAccount,
            user_name: str = None,
            # Имя пользователя, владеющего аккаунтом
            chat_url: str = None,
            chat_type: str = None,
            name: str = None,
    ):
        self.chat_id = chat_id
        self.social_account = social_account
        self.user_name = user_name
        self.chat_url = chat_url
        self.chat_type = chat_type
        self.name = name

    @abstractmethod
    async def get_messages(self):
        """Получает и возвращает список сообщений из чата."""
        pass

    @abstractmethod
    async def get_list_users(self):
        """Получает и возвращает список пользователей (участников) чата."""
        pass

    def __str__(self):
        return f"Chat(ID='{self.chat_id}', Type='{self.chat_type}', Social='{self.social_account_name}')"


# # _____________________________________________________________________________


class TelegramAccount(SocialAccount):
    def __init__(self, user: User, phone_number: str, api_id: str,
                 api_hash: str):

        # 2. Вызываем конструктор родительского класса SocialAccount
        #    передавая ему base_storage_path, social_name и phone_number
        super().__init__(
            name=SOCIAL_NETWORK_DICT.get(TELEGRAM_KEY),
            phone_number=phone_number
        )

        # 3. Инициализируем специфичные для TelegramAccount атрибуты
        self.user = user  # Сохраняем ссылку на объект User
        self.api_id = api_id
        self.api_hash = api_hash
        self.chats = {}

        # 4. Устанавливаем пути, используя pathlib.Path
        # user.storage_path - это папка пользователя
        # self.storage_path - это папка конкретного аккаунта, например "storage/JohnDoe/Telegram_12345"
        # self.session_path - это файл сессии, например "storage/JohnDoe/Telegram_12345/session_12345.session"

        # Путь для хранения данных конкретного Telegram-аккаунта
        # Используем self.social_name и self.phone_number для создания уникального пути
        self.storage_path = (
                user.storage_path / str(
            self.name) / f"{self.phone_number.replace('+', '')}"
        )

        # Путь к файлу сессии
        self.session_path = self.storage_path / SESSION_NAME_TEMPLATE.format(
            phone_number=self.phone_number.replace("+", "")
        )

        # 5. Инициализируем TelegramClient
        self.client = TelegramClient(
            str(self.session_path),
            # Telethon ожидает строковый путь к файлу сессии
            self.api_id,
            self.api_hash,
            # Дополнительные аргументы TelegramClient
            app_version=TELEGRAM_CLIENT_APP_VERSION,
            device_model=TELEGRAM_CLIENT_DEVICE_MODEL,
            system_version=TELEGRAM_CLIENT_SYSTEM_VERSION,
            lang_code=TELEGRAM_CLIENT_LANG_CODE,
            system_lang_code=TELEGRAM_CLIENT_SYSTEM_LANG_CODE,
        )

    async def connect(self):
        await self.client.start(phone=self.phone_number)
        logger.info(PRINT_CONNECT_MESSAGE)

    async def get_chats(self):
        return self.chats

    async def get_all_chats(self):
        """
        Получает и возвращает словарь всех чатов аккаунта из Telegram.

        :return: Словарь с именами чатов и их ID.
        """
        all_chats = {}
        async with self.client:
            async for dialog in self.client.iter_dialogs():
                if dialog.name:
                    all_chats[dialog.name] = dialog.id
        return all_chats

    async def add_chat(self, chat_obj):
        self.chats[chat_obj.chat_url] = chat_obj


# # _____________________________________________________________________________
class TelegramChat(Chat):
    def __init__(
            self, name: str | None, chat_id: int | str,
            social_account: TelegramAccount
    ):
        """
        Инициализация объекта TelegramChat.

        :param chat_id: Уникальный ID чата (числовой или строковый).
        """
        super().__init__(chat_id=chat_id, social_account=social_account,
                         name=name)
        # Эти поля можно заполнить позже, если они необходимы
        self.social_account = social_account

        self.chat_url = None
        self.chat_type = None

        self.name = name
        self.client = self.social_account.client
        self.entity = None
        self.storage_path = self.social_account.storage_path

    async def initialize(self):
        """
        Асинхронный метод для получения entity и завершения инициализации.
        Этот метод необходимо вызвать после создания объекта.
        """
        self.entity = await self.client.get_entity(self.chat_id)
        # При необходимости, здесь можно заполнить chat_url и chat_type
        # Например, если entity является каналом:
        if isinstance(self.entity, Channel):
            self.chat_type = CHAT_TYPE_CHANNEL_TEXT_TELETHON
            if getattr(self.entity, USERNAME_TEXT_TELETHON, None):
                self.chat_url = HTTPS_LINK_TEXT_CHAT_USERNAME + str(
                    self.entity.username
                )
            else:
                self.chat_url = HTTPS_LINK_TEXT_CHAT_ID + str(self.chat_id)
        else:
            self.chat_type = CHAT_TYPE_CHAT_TEXT_TELETHON
            # Для обычных чатов публичной ссылки нет
            self.chat_url = None

    async def get_messages(self):
        messages = []
        async for message in self.client.iter_messages(self.entity,
                                                       reverse=True):
            if not message.text:
                continue

            author_name = UNKNOWN_AUTHOR
            author_id = None
            if message.sender:
                sender_entity = await self.client.get_entity(message.sender)
                author_id = sender_entity.id

                if isinstance(sender_entity, TelethonUser):
                    if sender_entity.last_name:
                        author_name = FULL_NAME_TEMPLATE.format(
                            first_name=sender_entity.first_name,
                            last_name=sender_entity.last_name,
                        )
                    else:
                        author_name = sender_entity.first_name
                elif isinstance(sender_entity, (Channel, PeerChannel)):
                    author_name = getattr(
                        sender_entity, TELEGRAM_TITLE_ATTRIBUTE, UNKNOWN_AUTHOR
                    )
                else:
                    author_name = UNKNOWN_AUTHOR

            message_dict = {
                MESSAGE_ID_KEY: message.id,
                USER_ID_KEY: author_id,
                MESSAGE_TEXT_KEY: message.text,
                AUTHOR_NAME_KEY: author_name,
                DATE_KEY: message.date.isoformat(),
                REPLY_TO_ID_KEY: message.reply_to_msg_id,
            }
            messages.append(message_dict)
        return messages

    async def get_list_users(self):
        participants = await self.client.get_participants(self.entity)
        users = []
        for participant in participants:
            if participant.last_name:
                user_name = FULL_NAME_TEMPLATE.format(
                    first_name=participant.first_name,
                    last_name=participant.last_name
                )
            else:
                user_name = participant.first_name
            users.append(user_name)
        return users


# # _____________________________________________________________________________


class Knot:
    """
    Класс-узел, участник чата или сообщение
    """

    def __init__(self, unique_id: int, knot_type: KnotType, data: dict):
        self.unique_id = unique_id  # ID узла
        self.knot_type = knot_type  # Тип узла: пользователь или сообщение
        self.data = data  # данные (имя пользователя, текст сообщения и т.д.)
        self.outgoing_edges = (
            {}
        )  # Словарь исходящих связей (на кого/что направлена связь)
        self.incoming_edges = {}  # Словарь входящих связей (от кого/чего исходит связь)

    def add_edge(self, edge, is_outgoing=True):
        """Добавляет связь к узлу."""
        if is_outgoing:
            self.outgoing_edges[edge.unique_id] = edge
        else:
            self.incoming_edges[edge.unique_id] = edge

    def __str__(self):
        return (
            f"Knot(type={self.knot_type.name}, id={self.unique_id}, data='{self.data}')"
        )


# _____________________________________________________________________________
class Edge:
    """
    Класс-ребро, представляющее связь между двумя узлами.
    """

    def __init__(
            self,
            unique_id: int,
            sender_knot: Knot,
            receiver_knot: Knot,
            edge_type: EdgeType,
            content: str = None,
    ):
        self.unique_id = unique_id  # Уникальный ID ребра
        self.sender = sender_knot  # Отправитель связи (исходящий узел)
        self.receiver = receiver_knot  # Получатель связи (входящий узел)
        self.edge_type = (
            edge_type  # Тип связи: 'reply_to', 'mention', 'reaction', 'sent'
        )
        self.content = (
            content  # Содержание связи (например, "@username", "❤️", или None)
        )

    def __str__(self):
        return f"Edge(type={self.edge_type.name}, from={self.sender.unique_id} to={self.receiver.unique_id}, content='{self.content}')"
