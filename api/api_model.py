from pydantic import BaseModel
from typing import List, Optional
import datetime


class TwitchBotStatus(BaseModel):
    channel_names: List[str]
    mode: str
    osc_ip: str
    osc_port: str


class TwitchMessage(BaseModel):
    channel_name: str
    author_name: str
    author_id: str
    message_text: str
    is_command: Optional[bool]
    command_type: Optional[str]
    datetime: Optional[datetime.datetime]


class MessageListRequest(BaseModel):
    seconds_history: Optional[int]
    channel_names: Optional[List[str]]
