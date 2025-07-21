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
    user_stance: str
    bot_stance: str

HISTORY_LIMIT = 10



@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    conversation_id = request.conversation_id
    conversation: Optional[Conversation]
    
    # 1 - Retrive Conversation
    # 1.1 - Start a new conversation
    if not conversation_id:
        conversation = Conversation()
        conversation.save(db)
    else:
        # 1.2 - Get existing conversation from database
        conversation_obj = Conversation.get_by_id(db, conversation_id)

        if not isinstance(conversation_obj, Conversation):
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Cast to Conversation type
        conversation = cast(Conversation, conversation_obj)

        # Load messages from database
        conversation.load_messages_from_db(db, HISTORY_LIMIT)
    
    # 2 - Set Topic and Stance if not set yet
    if conversation.topic is None:
        # 2.1 - Extract User Topic and Stance
        topic = Topic.extract_user_topic_and_stance(request.message)

        if topic.topic.lower() != "unknown" and topic.user_stance.lower() != "Unknown":
            conversation.topic = topic.topic
            conversation.user_stance = topic.user_stance
            
            # 2.2 - Get bot stance
            bot_stance = Topic.extract_bot_stance(topic.topic, topic.user_stance)
            conversation.bot_stance = bot_stance.bot_stance
            
            conversation.save(db)

    # 3 - Add user message to database
    conversation.add_message_to_db(db, "user", request.message)
    
    # 4 - Create a debate instance
    debate = Debate(topic=str(conversation.topic), user_stance=str(conversation.user_stance), bot_stance=str(conversation.bot_stance))
    
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
            user_stance=str(conv.user_stance),
            bot_stance=str(conv.bot_stance)
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
