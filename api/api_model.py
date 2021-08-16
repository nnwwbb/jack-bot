from pydantic import BaseModel
from typing import List, Optional


class TwitchBotStatus(BaseModel):
    channel_names: List[str]
    mode: str


class TwitchMessage(BaseModel):
    channel_name: str
    author_name: str
    author_id: str
    message_text: str
    is_command: Optional[bool]
    command_type: Optional[str]


class MessageListRequest(BaseModel):
    seconds_history: Optional[int]
    channel_names: Optional[List[str]]
