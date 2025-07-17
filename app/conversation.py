from typing import List, Optional, Dict
import uuid

class Message:

    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}

class Conversation:

    def __init__(self, conversation_id: Optional[str] = None):
        self.id = conversation_id or str(uuid.uuid4())
        self.messages: List[Message] = []

    def add_message(self, message: Message) -> None:
        self.messages.append(message)

    def get_history(self, last_n: Optional[int] = None) -> List[Dict[str, str]]:
        msgs = self.messages[-last_n:] if last_n is not None else self.messages
        return [msg.to_dict() for msg in msgs]

