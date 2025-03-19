import requests
import json
from apollo.core.llm import Ollama
from apollo.utils.config import get_default_system_prompt
from typing import Optional, Dict, List, Any, Literal, Union, Callable, Type
from pydantic import BaseModel, Field
from apollo.tools.weather import get_weather
import re
import time


TOOL_REGISTRY = {
    "weather": {
        "name": "weather",
        "description": "Get current weather for a location using coordinates",
        "parameters": {
            "latitude": "number",
            "longitude": "number"
        },
        "implementation": get_weather
    }
}
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

def parse_json_response(text: str) -> AgentResponse:
    """
    Parse a text response that might contain JSON into an AgentResponse.
    
    This function tries different strategies to extract JSON:
    1. Try to parse the entire text as JSON
    2. Try to extract JSON from code blocks
    3. Otherwise, return the text as a plain response
    
    Args:
        text: The text response from the LLM
        
    Returns:
        An AgentResponse object
    """
    # Try direct JSON parsing
    try:
        data = json.loads(text)
        return AgentResponse(**data)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    try:
        # Match both ```json and ``` code blocks
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            return AgentResponse(**data)
    except (json.JSONDecodeError, AttributeError, IndexError):
        pass
    
    # If all else fails, return as plain text without tool calls
    return AgentResponse(response=text, tool_calls=None)

class Agent:
    def __init__(self,
                 llm: Optional[Ollama],
                 system_prompt: Optional[str] = None,                 
                 ):
        self.llm = llm if llm else Ollama()
        self.system_prompt = system_prompt if system_prompt else get_default_system_prompt()
        self.context = self.system_prompt
        self.history = []
        self.available_tools: Dict[str, Tool] = {}


    def query(self, prompt: str) -> AgentResponse:
        ''' 
        Query the agent with a prompt and return the response. 
        '''
        self.context += f"\n<start_of_turn>user\n{prompt}\n<end_of_turn>\n"
        tools_context = self._build_tools_context()
        input_text = f"{self.context}{tools_context}"
        print(input_text)
        response = self.llm.generate(input_text)
        self.history.append(response)
        return response
    
    def _build_tools_context(self) -> str:
        """
        Build a string describing the available tools.
        
        Returns:
            A string with tool descriptions
        """
        if not self.available_tools:
            return ""
            
        tools_context = "\nAvailable tools:\n"
        for tool in self.available_tools.values():
            tools_context += f"- {tool.name}: {tool.description}\n  Parameters: {tool.parameters}\n"
            
        return tools_context
    
    def register_tool(
        self, 
        name: str, 
        description: str, 
        parameters: Dict[str, Any],
        implementation: Optional[Callable] = None
    ):
        """
        Register a tool for the agent to use.
        
        Args:
            name: The tool name
            description: The tool description
            parameters: The parameters expected by the tool
            implementation: Optional function to execute when the tool is called
        """
        self.available_tools[name] = Tool(
            name=name,
            description=description,
            parameters=parameters
        )
        
        # if implementation:
        #   self.tool_implementations[name] = implementation

def main():
    ollama_agent = Agent(llm=Ollama())

    # Register tools from the registry
    print("Registering tools...")
    for tool_id, tool_info in TOOL_REGISTRY.items():
        ollama_agent.register_tool(
            name=tool_info["name"],
            description=tool_info["description"],
            parameters=tool_info["parameters"],
            implementation=tool_info["implementation"]
        )
    print(ollama_agent.available_tools)
    while True:
        user_input = input(f"{'User':<10}: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            print(ollama_agent.context)
            break
            
        response = ollama_agent.query(user_input)
        resp = parse_json_response(response)
        print(f"{'Agent':<10}: {resp.response}")
        if resp.tool_calls:
            print("Tools to call:")
            for tool_call in resp.tool_calls:
                print(f"  {tool_call.tool_name}: {tool_call.parameters}")
        


if __name__ == "__main__":
    main()