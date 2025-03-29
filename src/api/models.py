from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    role: MessageRole
    content: str
    persona: Optional[str] = None  # Which persona is responding (if applicable)
    timestamp: datetime = datetime.now()

class ChatSession(BaseModel):
    session_id: str
    property_data: Dict
    distance_info: Optional[Dict] = None
    messages: List[Message] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # If None, creates new session
    property_url: Optional[str] = None  # Required for new sessions

class ChatResponse(BaseModel):
    session_id: str
    messages: List[Message]
    property_data: Optional[Dict] = None
    distance_info: Optional[Dict] = None 