from app.openai_response import OpenAI_Response
import json

class Topic:
    def __init__(self, topic: str, user_stance: str, bot_stance: str):
        self.topic = topic
        self.user_stance = user_stance
        self.bot_stance = bot_stance

    @classmethod
    def extract_user_topic_and_stance(cls, user_message: str) -> 'Topic':
        openai_response = OpenAI_Response()
        system_prompt = (
            "You are an assistant that extracts a debate topic and a user'stance from a user's message. "
            "Sometimes the user's message is not a debate topic with a stance, but a question, a statement or a greeting. "
            "For example: Hello. How are you today? Are you ready to lose the debate? "
            "In that case, you cannot extract a stance and a topic, you should return Unknown for both."
            "The topic should be a debatable subject, and the stance should be a clear user's position on that topic."
            "Do not create a topic or a stance that is not related to the user's message. Return Unknown for both if that is the case."
            "Return your answer in the following JSON format: {\"topic\": \"...\", \"user_stance\": \"...\"}. "
            
        )
        conversation_history = [
            {"role": "user", "content": user_message}
        ]
        result = openai_response.get_response(system_prompt, conversation_history)
        
        try:
            data = json.loads(result)
            return cls(topic=data.get("topic", "Unknown"), user_stance=data.get("user_stance", "Unknown"), bot_stance="Be oposite to user's stance")
        except Exception:
            return cls(topic="Unknown", user_stance="Unknown", bot_stance="Be oposite to user's stance")
    
    @classmethod
    def extract_bot_stance(cls, topic: str, user_stance: str) -> 'Topic':
        openai_response = OpenAI_Response()
        system_prompt = (
            "You are an assistant that sets the bot's stance based on the user's stance and the debate topic."
            "The debate topic is: {topic}"
            "The user's stance is: {user_stance}"
            "The bot's stance should be opposite to the user's stance related to the topic and clear."
            "Return your answer in the following JSON format: {\"bot_stance\": \"...\"}. "
        )
        conversation_history = [
            {"role": "user", "content": f"Topic: {topic}\nUser Stance: {user_stance}"}
        ]
        result = openai_response.get_response(system_prompt, conversation_history)

        try:
            data = json.loads(result)
            return cls(topic = topic, user_stance = user_stance, bot_stance=data.get("bot_stance", "Be oposite to user's stance"))
        except Exception:
            return cls(topic = topic, user_stance = user_stance, bot_stance="Be oposite to user's stance")
