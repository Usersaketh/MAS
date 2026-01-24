from ollama import Client

from app.core.config import settings


class OllamaService:
    def __init__(self) -> None:
        self.client = Client(host=settings.ollama_base_url)
        self.model = settings.ollama_model

    def generate(self, prompt: str) -> str:
        response = self.client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]
