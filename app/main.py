from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, cast
from sqlalchemy.orm import Session
from app.topic import Topic
from app.conversation import Conversation
from app.debate import Debate
from app.database import get_db, engine, Base
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Use FastAPI lifespan event handler for automatic table creation
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str

class ChatMessage(BaseModel):
    role: str
    message: str

class ChatResponse(BaseModel):
    conversation_id: str
    message: List[ChatMessage]

class ConversationSummary(BaseModel):
    id: str
    topic: str
    stance: str

HISTORY_LIMIT = 10



@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    conversation_id = request.conversation_id
    conversation: Optional[Conversation]

    # Start a new conversation
    if not conversation_id:
        topic = Topic.extract_topic_and_stance(request.message)
        conversation = Conversation(topic=topic.topic, stance=topic.stance)
        conversation.save(db)
    else:
        # Get existing conversation from database
        conversation_obj = Conversation.get_by_id(db, conversation_id)
        if not isinstance(conversation_obj, Conversation):
            raise HTTPException(status_code=404, detail="Conversation not found")
        conversation = cast(Conversation, conversation_obj)
        # Load messages from database
        conversation.load_messages_from_db(db, HISTORY_LIMIT)
    
    # Add user message to database
    conversation.add_message_to_db(db, "user", request.message)
    
    # Create a debate instance
    debate = Debate(topic=str(conversation.topic), stance=str(conversation.stance))
    
    # Get conversation history for the debate
    history = conversation.get_history_dict(HISTORY_LIMIT)
    
    # Get bot reply
    bot_reply = debate.chat(request.message, history)
    
    # Error handling for AI API
    if isinstance(bot_reply, str) and bot_reply.startswith("Error:"):
        raise HTTPException(status_code=502, detail=bot_reply)
    
    # Add bot reply to database
    conversation.add_message_to_db(db, "assistant", bot_reply)

    # Reload messages from DB to refresh the in-memory list
    conversation.load_messages_from_db(db, HISTORY_LIMIT)

    # Use only the last HISTORY_LIMIT messages for the response
    formatted_history = [
        ChatMessage(
            role=(msg["role"] if msg["role"] != "assistant" else "bot"),
            message=msg["content"]
        )
        for msg in conversation.get_history_dict(HISTORY_LIMIT)
    ]

    return ChatResponse(
        conversation_id=str(conversation.id),
        message=formatted_history
    )

@app.get("/conversations", response_model=List[ConversationSummary])
def list_conversations(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max items to return")
):
    conversations = db.query(Conversation).offset(skip).limit(limit).all()
    return [
        ConversationSummary(
            id=str(conv.id),
            topic=str(conv.topic),
            stance=str(conv.stance)
        )
        for conv in conversations
    ]

@app.get("/conversations/{conversation_id}/messages", response_model=List[ChatMessage])
def list_conversation_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max items to return"),
    desc: bool = Query(False, description="Sort from newest to oldest if true, oldest to newest if false")
):
    conversation = Conversation.get_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    # Load all messages in the requested order
    all_messages = conversation.load_all_messages_from_db(db, desc=desc)
    paginated = all_messages[skip:skip+limit]
    return [
        ChatMessage(
            role=(msg.role if msg.role != "assistant" else "bot"),
            message=msg.content
        )
        for msg in paginated
    ]

@app.get("/")
def root():
    return JSONResponse({
        "message": "Welcome to the Debate Chatbot API!",
        "docs": "/docs",
        "info": "See /docs for interactive API documentation."
    })
