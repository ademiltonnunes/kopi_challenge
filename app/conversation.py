import datetime
from typing import List, Optional
import uuid
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with conversation
    conversation = relationship("Conversation", back_populates="messages")

    def __init__(self, role: str, content: str, timestamp: Optional[datetime.datetime] = None):
        self.role = role
        self.content = content
        self.timestamp = timestamp if timestamp is not None else datetime.datetime.now()

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    topic = Column(Text, nullable=False)
    stance = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with messages
    messages = relationship("Message", back_populates="conversation")

    def __init__(self, conversation_id: Optional[str] = None, topic: Optional[str] = None, stance: Optional[str] = None):
        self.id = conversation_id or str(uuid.uuid4())
        self.topic = topic
        self.stance = stance
        self.messages: List[Message] = []

    def get_history_dict(self, last_n: Optional[int] = None) -> List[dict]:
        msgs = self.messages[-last_n:] if last_n is not None else self.messages
        return [msg.to_dict() for msg in msgs]

    # Database operations
    def save(self, db_session):
        """Save conversation to database"""
        db_session.add(self)
        db_session.commit()
        db_session.refresh(self)
        return self

    @classmethod
    def get_by_id(cls, db_session, conversation_id: str):
        """Get conversation by ID from database"""
        return db_session.query(cls).filter(cls.id == conversation_id).first()

    def add_message_to_db(self, db_session, role: str, content: str) -> Message:
        """Add a message to the conversation and save to database"""
        message = Message(role=role, content=content)
        message.conversation_id = self.id
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        return message

    def load_messages_from_db(self, db_session, limit: int = 10):
        """Load the most recent messages from database, in chronological order (oldest to newest)"""
        messages = db_session.query(Message)\
            .filter(Message.conversation_id == self.id)\
            .order_by(Message.id.desc())\
            .limit(limit)\
            .all()
        messages = list(reversed(messages))  # So oldest is first
        return messages

    def load_all_messages_from_db(self, db_session, desc: bool = False):
        """Load all messages from database, ordered by id. If desc=True, newest to oldest."""
        query = db_session.query(Message).filter(Message.conversation_id == self.id)
        if desc:
            query = query.order_by(Message.id.desc())
        else:
            query = query.order_by(Message.id.asc())
        messages = query.all()
        return messages
