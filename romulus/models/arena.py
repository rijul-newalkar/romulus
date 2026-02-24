from datetime import date, datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class FitnessScore(BaseModel):
    agent_id: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success_rate_7d: float = 0.0
    avg_confidence_calibration: float = 0.0
    avg_latency_ms: float = 0.0
    vigil_incident_rate: float = 0.0
    composite_fitness: float = 0.0


class PerformanceSnapshot(BaseModel):
    date: date
    total_tasks: int = 0
    successful_tasks: int = 0
    success_rate: float = 0.0
    avg_confidence: float = 0.0
    avg_latency_ms: float = 0.0
    vigil_incidents: int = 0
    composite_fitness: float = 0.0
