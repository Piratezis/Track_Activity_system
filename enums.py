from enum import Enum


class MessageKeys(str, Enum):
    MESSAGE_ID = "message_id"
    USER_ID = "user_id"
    REPLY_TO_ID = "reply_to_message_id"
    MESSAGE_TEXT = "message_text"
    AUTHOR_NAME = "author_name"
    DATE = "date"
    REACTIONS = "reactions"
    MENTIONS = "mentions"


class KnotType(str, Enum):
    USER = "user"
    MESSAGE = "message"


class EdgeType(str, Enum):
    REPLY_TO = "reply_to"
    MENTION = "mention"
    REACTION = "reaction"
    SENT = "sent"
