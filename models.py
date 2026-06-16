from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    session_id: str
    message: str
    user_id: Optional[int] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    response_type: str
    session_id: str