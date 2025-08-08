import pathlib
from abc import ABC, abstractmethod
from telethon import TelegramClient
from telethon.tl.types import PeerChannel, Channel, User as TelethonUser


# ______________________________________________________________________
class User:
    def __init__(self, name, phone_number, storage_dir):
        self.name = name
        self.phone_number = phone_number
        self.social_accounts = []
        self.storage_path = storage_dir / self.name
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def get_social_accounts(self):
        return self.social_accounts

    def add_social_account(self, account):
        self.social_accounts.append(account)

    def __str__(self):
        return f"User(name='{self.name}', phone='{self.phone_number}')"


class SocialAccount(ABC):
    def __init__(self, user, api_id, api_hash):
        self.user = user
        self.api_id = api_id
        self.api_hash = api_hash
        self.storage_path = self.user.storage_path / self.__class__.__name__
        self.storage_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def get_chats(self):
        pass

    @abstractmethod
    async def add_chat(self, chat_url):
        pass


class Chat(ABC):
    def __init__(self, chat_url, social_account_name, user_name):
        self.chat_url = chat_url
        chat_filename = chat_url.replace('https://t.me/', '').replace('/',
                                                                      '_') + '.json'
        self.storage_path = pathlib.Path(
            'storage') / user_name / social_account_name / chat_filename
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def get_messages(self):
        pass

    @abstractmethod
    async def get_list_users(self):
        pass


# _____________________________________________________________________________

class TelegramAccount(SocialAccount):
    def __init__(self, user, api_id, api_hash):
        super().__init__(user, api_id, api_hash)
        self.chats = {}
        session_path = self.user.storage_path / f"{self.user.phone_number}_session"
        self.client = TelegramClient(
            str(session_path),
            self.api_id,
            self.api_hash,
            app_version="4.16.8-telethon",
            device_model="Windows 10",
            system_version="10",
            lang_code="en",
            system_lang_code="en"
        )
        
    async def connect(self):
        await self.client.start(phone=self.user.phone_number)
        print("Конект в телеге")
        self.user.add_social_account(self)

    async def get_chats(self):
        return self.chats

    async def add_chat(self, chat_url):
        entity = await self.client.get_entity(chat_url)
        chat_obj = TelegramChat(self.client, entity, chat_url,
                                self.__class__.__name__, self.user.name)
        self.chats[chat_url] = chat_obj
        print("чат добавлен")
        return chat_obj


class TelegramChat(Chat):
    def __init__(self, client, entity, chat_url, social_account_name,
                 user_name):
        super().__init__(chat_url, social_account_name, user_name)
        self.client = client
        self.entity = entity

    async def get_messages(self):
        messages = []
        async for message in self.client.iter_messages(self.entity,
                                                       reverse=True):
            if not message.text:
                continue

            author_name = "Неизвестный"
            author_id = None
            if message.sender:
                sender_entity = await self.client.get_entity(message.sender)
                author_id = sender_entity.id

                if isinstance(sender_entity, TelethonUser):
                    author_name = sender_entity.first_name
                    if sender_entity.last_name:
                        author_name += f" {sender_entity.last_name}"
                elif isinstance(sender_entity, (Channel, PeerChannel)):
                    author_name = getattr(sender_entity, 'title',
                                          'Неизвестный')
                else:
                    author_name = "Неизвестный"

            message_dict = {
                'message_id': message.id,
                'user_id': author_id,
                'message_text': message.text,
                'author_name': author_name,
                'date': message.date.isoformat(),
                'reply_to_message_id': message.reply_to_msg_id
            }
            messages.append(message_dict)
        return messages

    async def get_list_users(self):
        participants = await self.client.get_participants(self.entity)
        users = []
        for participant in participants:
            user_name = participant.first_name
            if participant.last_name:
                user_name += f" {participant.last_name}"
            users.append(user_name)
        return users
