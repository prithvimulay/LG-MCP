"""
LangChain integration for PDF-to-Podcast conversion
"""

import os
from typing import Optional, Dict, Any
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory

from .config.settings import settings

class LangChainManager:
    """Manages LangChain integration for podcast generation"""
    
    def __init__(self):
        self._llm = None
        self._setup_llm()
    
    def _setup_llm(self):
        """Initialize the Groq LLM"""
        api_key = settings.groq_api_key or os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError(
                "Groq API key not found. Set GROQ_API_KEY environment variable "
                "or configure groq_api_key in settings"
            )
        
        self._llm = ChatGroq(
            groq_api_key=api_key,
            model_name=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens
        )
    
    @property
    def llm(self) -> ChatGroq:
        """Get the LLM instance"""
        if self._llm is None:
            self._setup_llm()
        return self._llm
    
    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a response using the LLM"""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def create_podcast_agent(self, tools: list) -> AgentExecutor:
        """Create a LangChain agent for podcast generation"""
        
        system_prompt = """
        You are a professional podcast creator and content strategist.
        You specialize in transforming PDF content into engaging podcast scripts.
        
        Your capabilities include:
        - Analyzing PDF content for key themes and insights
        - Creating interview-style podcast scripts
        - Generating educational podcast content
        - Structuring content for optimal listener engagement
        - Converting complex topics into accessible narratives
        
        Always provide well-structured, engaging content that respects the source material
        while making it accessible to a general audience.
        """
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create memory for conversation
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create the agent
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the LLM connection"""
        try:
            response = self.generate_response(
                system_prompt="You are a helpful assistant.",
                user_prompt="Say hello and confirm you're working correctly."
            )
            return {
                "success": True,
                "message": "LLM connection successful",
                "response": response,
                "model": settings.llm_model
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"LLM connection failed: {str(e)}",
                "error": str(e)
            }

# Global instance
langchain_manager = LangChainManager()
