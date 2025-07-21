from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAI_Response:
    def __init__(self, model: str = "o4-mini", temperature: float = 0.5, max_tokens: int = 1000):
        self.client = OpenAI()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def get_completion(self, system_prompt: str, conversation_history: list[dict[str, str]])->str:

        messages = [{
            "role": "system",
            "content": system_prompt
        }] + conversation_history

        try:

            response = self.client.chat.completions.create(
                model = self.model,
                messages = messages,
                temperature = self.temperature,
                max_tokens = self.max_tokens
            )

            content = response.choices[0].message.content

            return content if content else ""
        except Exception as e:
            return "Error: " + str(e)
    
    def get_response(self, system_prompt: str, conversation_history: list[dict[str, str]])->str:

        messages = [{
            "role": "system",
            "content": system_prompt
        }] + conversation_history

        try:

            response = self.client.responses.create(
                model = self.model,
                input = messages,
            )

            content = response.output_text

            return content if content else ""
        except Exception as e:
            return "Error: " + str(e)

def main():
    openai_response = OpenAI_Response()
    print(openai_response.get_completion("I am testing the openai api", [{"role": "user", "content": "Hello, how are you?"}]))
    print(openai_response.get_response("I am testing the openai api", [{"role": "user", "content": "Hello, how are you?"}]))

if __name__ == "__main__":
    main()