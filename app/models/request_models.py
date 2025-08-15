from pydantic import BaseModel
from typing import Optional, Dict, Any


class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class HealthCheckRequest(BaseModel):
    service: Optional[str] = None
