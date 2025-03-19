from pydantic import BaseModel, Field
import requests
from typing import Optional, List, Dict, Any

class Tool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class ToolCall(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

class AgentResponse(BaseModel):
    response: str = Field(description="The text response from the agent")
    tool_calls: Optional[List[ToolCall]] = Field(default=None, description="List of tools to be called")

class OllamaAgent:
    def __init__(self, model="gemma3:12b", system_prompt=None):
        self.base_url = "http://localhost:11434/api/generate"
        self.model = model
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = """You are a helpful AI assistant. When you need to use tools, format your response as JSON with the following structure:
{
    "response": "your explanation of what you're doing",
    "tool_calls": [
        {
            "tool_name": "name_of_tool",
            "parameters": {
                "param1": "value1",
                "param2": "value2"
            }
        }
    ]
}
Be careful to use tools when you really can, tool_use = true implies that tool_calls is not None.
If you don't need to use any tools, respond with:
{
    "response": "your normal response"
    "tool_calls": []
}

be concise and clear, only use tools when necessary."""
        self.context = ''
        self.available_tools: Dict[str, Tool] = {}

    def register_tool(self, name: str, description: str, parameters: Dict[str, Any]):
        """Register a new tool that the agent can use"""
        self.available_tools[name] = Tool(
            name=name,
            description=description,
            parameters=parameters
        )

    def query_ollama(self, prompt: str) -> AgentResponse:
        """Query the Ollama model and return a structured response"""
        tools_context = "\nAvailable tools:\n"
        for tool in self.available_tools.values():
            tools_context += f"- {tool.name}: {tool.description}\n  Parameters: {tool.parameters}\n"
        
        if self.context.strip() == "":
            self.context = self.system_prompt + tools_context

        self.context = self.context + "\nUser: " + prompt

        data = {
            "model": self.model,
            "prompt": self.context,
            "stream": False
        }
        
        response = requests.post(self.base_url, json=data)
        raw_response = response.json()['response']
        self.context = self.context + "\nAgent: " + raw_response

        try:
            # Try to parse the response as JSON
            import json
            response_dict = json.loads(raw_response)
            return AgentResponse(**response_dict)
        except json.JSONDecodeError:
            # If the response isn't JSON, wrap it in our structure
            return AgentResponse(
                response=raw_response,
                tool_calls=[]
            )

def main():
    # Initialize agent
    agent = OllamaAgent()
    
    # Register some example tools
    agent.register_tool(
        name="weather",
        description="Get the current weather for a location",
        parameters={"lat": "string", "long": "string"}
    )
    
    agent.register_tool(
        name="calculator",
        description="Perform mathematical calculations",
        parameters={"expression": "string"}
    )

    while True:
        user_input = input(f"{'User':<10}: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            print(agent.context)
            break
            
        response = agent.query_ollama(user_input)
        print(f"{'Agent':<10}: {response.response}")
        
        if response.tool_calls:
            print("Tool calls requested:")
            for tool_call in response.tool_calls:
                print(f"- {tool_call.tool_name}: {tool_call.parameters}")

if __name__ == "__main__":
    main()