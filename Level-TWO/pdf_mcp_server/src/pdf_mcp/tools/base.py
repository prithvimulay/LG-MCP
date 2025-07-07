"""
Minimal base tool for MVP
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """Simple base class for MCP tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """Execute the tool and return result string"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return {
            "name": self.name,
            "description": self.description
        }


def tool(name: str, description: str):
    """Simple decorator for creating tools"""
    def decorator(func):
        func._tool_name = name
        func._tool_description = description
        return func
    return decorator