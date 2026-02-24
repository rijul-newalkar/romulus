from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from romulus.models.semantic import SemanticRule


class DreamReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    date: datetime = Field(default_factory=datetime.utcnow)
    episodes_processed: int = 0
    counterfactuals_run: int = 0
    new_rules_extracted: list[SemanticRule] = []
    rules_invalidated: list[str] = []
    memories_pruned: int = 0
    weak_spots_found: list[str] = []
    confidence_adjustment: float = 0.0
    summary: str = ""
