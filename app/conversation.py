import datetime
from typing import List, Optional
import uuid

class Message:

    def __init__(self, role: str, content: str, timestamp: Optional[datetime.datetime] = None):
        self.role = role
        self.content = content
        self.timestamp = timestamp if timestamp is not None else datetime.datetime.now()

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}

class Conversation:

    def __init__(self, conversation_id: Optional[str] = None, topic: Optional[str] = None, stance: Optional[str] = None):
        self.id = conversation_id or str(uuid.uuid4())
        self.topic = topic
        self.stance = stance
        self.messages: List[Message] = []

    def add_message(self, message: Message) -> None:
        self.messages.append(message)

    def get_history(self, last_n: Optional[int] = None) -> List[Message]:
        msgs = self.messages[-last_n:] if last_n is not None else self.messages
        return msgs

    def get_history_dict(self, last_n: Optional[int] = None) -> List[dict]:
        msgs = self.messages[-last_n:] if last_n is not None else self.messages
        return [msg.to_dict() for msg in msgs]
