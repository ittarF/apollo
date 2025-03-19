"""
This module contains the implementation of the LLM class.
"""
import requests
import json

class Ollama:
    
    def __init__(self, 
                 model="gemma3:12b",
                 base_url="http://localhost:11434/api/generate"):
        self.model = model
        self.base_url = base_url

    def generate(self,
                 text: str,
                 max_tokens: int = 1024,
                 temperature: float = 0.7) -> str:
        payload = {
            "model": self.model,
            "prompt": text,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }

        response = requests.post(self.base_url, json=payload)
        response_data = json.loads(response.text)
        if "response" in response_data:
            return response_data["response"]
        else:
            return response.text


if __name__ == "__main__":
    ollama = Ollama()
    ollama.generate("Hi, how are you?")