from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class QueryResponse(BaseModel):
    response: str
    session_id: str
    processing_node: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    timestamp: datetime
    success: bool = True


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime
    success: bool = False


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]
    version: str = "1.0.0"


class IntentAnalysisResponse(BaseModel):
    intent: str
    confidence: float
    reasoning: str


class RAGRetrievalResponse(BaseModel):
    context: str
    retrieved_documents: int
    relevance_scores: List[float]
