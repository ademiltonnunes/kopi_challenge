import pytest
from app.openai_response import OpenAI_Response

class MockChatCompletions:
    @staticmethod
    def create(model, messages, temperature, max_tokens):
        class MockChoices:
            def __init__(self):
                self.message = type('obj', (object,), {'content': 'Mocked response'})
        class MockResponse:
            def __init__(self):
                self.choices = [MockChoices()]
        return MockResponse()

class MockClient:
    def __init__(self):
        self.chat = type('obj', (object,), {'completions': MockChatCompletions})

def test_get_completion(monkeypatch):
    openai_response = OpenAI_Response()
    openai_response.client = MockClient()
    result = openai_response.get_completion(
        "Test system prompt",
        [{"role": "user", "content": "Test message"}]
    )
    assert result == "Mocked response" 