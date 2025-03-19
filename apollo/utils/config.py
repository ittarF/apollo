"""
Configuration utilities for the Agent Framework.
"""

def get_default_system_prompt() -> str:
    """
    Get the default system prompt for agents.
    
    Returns:
        The default system prompt
    """
    return """You are a helpful AI assistant. When you need to use tools, format your response as JSON codeblock with the following structure:
```json
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
}.
If you don't need to use any tools, respond with:
{
    "response": "your normal response",
    "tool_calls": []
}
```
Be concise and clear, only use tools when you can for more accuracy."""