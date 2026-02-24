from enum import Enum

from pydantic import BaseModel


class ThreatCategory(str, Enum):
    DESTRUCTIVE = "destructive"
    LOOPING = "looping"
    HALLUCINATION = "hallucination"
    SCOPE_ESCAPE = "scope_escape"
    COST_RUNAWAY = "cost_runaway"
    CONFIDENCE_ANOMALY = "confidence_anomaly"
    CASCADE_RISK = "cascade_risk"


class VigilVerdict(BaseModel):
    approved: bool
    category: ThreatCategory | None = None
    layer: str = ""
    reason: str = ""
    latency_ms: int = 0
