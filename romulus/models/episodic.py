from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class EpisodicTrace(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    task: str
    context: dict = {}
    decision: str
    tools_used: list[str] = []
    outcome: str
    success: bool
    confidence: float
    latency_ms: int = 0
    tokens_used: int = 0
    alternatives_considered: list[str] = []


class TaskResult(BaseModel):
    task: str
    success: bool
    confidence: float
    response: str
    vigil_flags: list[str] = []
    tokens_used: int = 0
    latency_ms: int = 0
