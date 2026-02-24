from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentIdentity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    version: str = "0.1.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    soul_spec: str = ""
    total_tasks: int = 0
    successful_tasks: int = 0
    trust_score: float = 0.5
    total_uptime_seconds: int = 0
