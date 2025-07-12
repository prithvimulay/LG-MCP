"""
Simple session model for MVP
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

class ConversationState(BaseModel):
    """State model for LangGraph conversation flow"""
    query: str
    pdf_path: Optional[str] = None
    response: Optional[str] = None


class UserSession(BaseModel):
    """Simple user session for maintaining state"""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = "default_user"
    last_query: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SessionManager:
    """Simple session manager"""
    
    def __init__(self, mongo_manager):
        self.mongo = mongo_manager
        self.sessions_collection = self.mongo.db.sessions
        self.current_session: Optional[UserSession] = None
    
    def get_session(self) -> UserSession:
        """Get or create current session"""
        if not self.current_session:
            self.current_session = UserSession()
        return self.current_session
    
    def update_last_query(self, query: str):
        """Update last query in session"""
        session = self.get_session()
        session.last_query = query
        session.updated_at = datetime.utcnow()