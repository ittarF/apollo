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
                 temperature: float = 0.7,
                 stream: bool = False) -> str:
        payload = {
            "model": self.model,
            "prompt": text,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }

        if payload.get("stream"):
            # Send the POST request with streaming enabled
            response = requests.post(self.base_url, json=payload, stream=True)

            # Process the stream
            buffer = ""  # Buffer for displaying text
            complete_response = ""  # String to store the entire response

            for line in response.iter_lines():
                if line:  # Filter out empty lines
                    chunk = json.loads(line.decode('utf-8'))
                    if "response" in chunk:
                        content = chunk["response"]
                        
                        # Add to the complete response
                        complete_response += content
                        
                        # Handle display buffer
                        buffer += content
                        
                        # Check if buffer contains a newline
                        if "\n" in buffer:
                            parts = buffer.split("\n")
                            # Print all complete parts except the last one
                            for part in parts[:-1]:
                                print(part, flush=True)
                            # Keep the incomplete part in the buffer
                            buffer = parts[-1]
                        # Also check for word boundaries
                        elif buffer.endswith(" ") or buffer.endswith(".") or buffer.endswith(","):
                            print(buffer, end="", flush=True)
                            buffer = ""
                            
                    if chunk.get("done"):
                        # Print any remaining buffer
                        if buffer:
                            print(buffer, end="")
                        print()  # New line at the end
                        break
        else:
            response = requests.post(self.base_url, json=payload)
            response_data = json.loads(response.text)
            if "response" in response_data:
                print(response_data["response"])
                return response_data["response"]
            else:
                print(response.text)
                return response.text


if __name__ == "__main__":
    ollama = Ollama()
    ollama.generate("Hi, how are you?", stream=True)