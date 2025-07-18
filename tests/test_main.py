import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "docs" in resp.json()

def test_chat_new_conversation():
    resp = client.post("/chat", json={"conversation_id": None, "message": "Is AI dangerous?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "conversation_id" in data
    assert isinstance(data["message"], list)
    assert data["message"][-1]["role"] == "bot"

def test_chat_existing_conversation():
    # Start a new conversation
    resp1 = client.post("/chat", json={"conversation_id": None, "message": "Is the Earth flat?"})
    conv_id = resp1.json()["conversation_id"]
    # Continue the conversation
    resp2 = client.post("/chat", json={"conversation_id": conv_id, "message": "Why do you think so?"})
    assert resp2.status_code == 200
    assert resp2.json()["conversation_id"] == conv_id

def test_list_conversations():
    resp = client.get("/conversations")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_list_conversation_messages():
    # Start a new conversation
    resp1 = client.post("/chat", json={"conversation_id": None, "message": "Test message"})
    conv_id = resp1.json()["conversation_id"]
    # Get messages
    resp2 = client.get(f"/conversations/{conv_id}/messages")
    assert resp2.status_code == 200
    messages = resp2.json()
    assert isinstance(messages, list)
    assert any(msg["role"] == "user" for msg in messages)
    assert any(msg["role"] == "bot" for msg in messages)

def test_list_conversation_messages_not_found():
    resp = client.get("/conversations/doesnotexist/messages")
    assert resp.status_code == 404

def test_chat_conversation_not_found():
    resp = client.post("/chat", json={"conversation_id": "doesnotexist", "message": "Hello"})
    assert resp.status_code == 404 