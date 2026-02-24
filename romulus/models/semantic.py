from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class SemanticRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    rule: str
    confidence: float
    evidence_count: int = 1
    last_validated: datetime = Field(default_factory=datetime.utcnow)
    contradictions: int = 0
    domain: str = "general"
    source_episode_ids: list[str] = []
