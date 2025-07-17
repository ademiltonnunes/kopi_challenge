from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from app.topic import Topic
from app.conversation import Conversation, Message
from app.debate import Debate

app = FastAPI()

# In-memory conversation store
conversations: Dict[str, Conversation] = {}

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str

class ChatMessage(BaseModel):
    role: str
    message: str

class ChatResponse(BaseModel):
    conversation_id: str
    message: list[ChatMessage]

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    conversation_id = request.conversation_id if request.conversation_id is not None else None

    # Start a new conversation
    if not conversation_id:
        topic = Topic.extract_topic_and_stance(request.message)
        conversation = Conversation(topic=topic.topic, stance=topic.stance)
        conversations[conversation.id] = conversation
    # Continue an existing conversation
    else:
        conversation = conversations.get(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Add user message
    conversation.add_message(Message("user", request.message))
    # Create a debate instance
    debate = Debate(topic=conversation.topic, stance=conversation.stance)
    # Get bot reply
    bot_reply = debate.chat(conversation)
    # Add bot reply to conversation
    conversation.add_message(Message("assistant", bot_reply))

    # Convert Message objects to ChatMessage for the response
    formatted_history = [
        ChatMessage(role=msg.role, message=msg.content) for msg in conversation.get_history(last_n=10)
    ]

    return ChatResponse(
        conversation_id=conversation.id,
        message=formatted_history
    )
