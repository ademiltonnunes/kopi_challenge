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
    conversation_id: Optional[str]
    message: str

class ChatMessage(BaseModel):
    role: str
    message: str

class ChatResponse(BaseModel):
    conversation_id: str
    message: list[ChatMessage]

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    # If no conversation_id, start a new conversation and extract topic/stance
    if not request.conversation_id:
        topic = Topic.extract_topic_and_stance(request.message)
        conversation = Conversation(topic=topic.topic, stance=topic.stance)
        conversations[conversation.id] = conversation
        # Add initial user message
        conversation.add_message(Message("user", request.message))
        # Create Debate instance with extracted topic/stance
        debate = Debate(topic=topic.topic, stance=topic.stance)
    else:
        conversation = conversations.get(request.conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        # Add user message
        conversation.add_message(Message("user", request.message))
        # Use stored topic/stance (assuming stance is stored or can be reconstructed)
        # For now, use a default stance if not available
        debate = Debate(topic=conversation.topic, stance=conversation.stance)

    # Get bot reply
    bot_reply = debate.chat(conversation)
    conversation.add_message(Message("assistant", bot_reply))

    # Return the last 10 messages (most recent last)
    history = conversation.get_history()[-10:]
    formatted_history = [
        ChatMessage(role=msg["role"], message=msg["content"]) for msg in history
    ]
    return ChatResponse(
        conversation_id=conversation.id,
        message=formatted_history
    )
