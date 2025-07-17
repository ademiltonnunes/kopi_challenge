from app.openai_response import OpenAI_Response
import json

class Topic:
    def __init__(self, topic: str, stance: str):
        self.topic = topic
        self.stance = stance

    @classmethod
    def extract_topic_and_stance(cls, user_message: str) -> 'Topic':
        openai_response = OpenAI_Response()
        system_prompt = (
            "You are an assistant that extracts a debate topic and a stance from a user's message. "
            "Return your answer in the following JSON format: {\"topic\": \"...\", \"stance\": \"...\"}. "
            "The topic should be a debatable subject, and the stance should be a clear position on that topic."
        )
        conversation_history = [
            {"role": "user", "content": user_message}
        ]
        result = openai_response.get_completion(system_prompt, conversation_history)
        
        try:
            data = json.loads(result)
            return cls(topic=data.get("topic", "Unknown"), stance=data.get("stance", "Unknown"))
        except Exception:
            return cls(topic="General Debate", stance="Affirmative")
