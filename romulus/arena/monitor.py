from datetime import date, datetime, timedelta

from romulus.chronicle.episodic import EpisodicStore
from romulus.models.arena import FitnessScore, PerformanceSnapshot
from romulus.vigil.incidents import IncidentLogger


class FitnessMonitor:
    def __init__(self, episodic_store: EpisodicStore, incident_logger: IncidentLogger):
        self.episodic = episodic_store
        self.incidents = incident_logger

    async def compute_fitness(self, window_days: int = 7) -> FitnessScore:
        since = datetime.utcnow() - timedelta(days=window_days)
        traces = await self.episodic.get_traces(since=since, limit=1000)

        if not traces:
            return FitnessScore()

        total = len(traces)
        successes = sum(1 for t in traces if t.success)
        success_rate = successes / total

        avg_confidence = sum(t.confidence for t in traces) / total
        actual_success_rate = success_rate
        calibration = 1.0 - abs(avg_confidence - actual_success_rate)

        avg_latency = sum(t.latency_ms for t in traces) / total

        incident_count = await self.incidents.get_incident_count(hours=window_days * 24)
        incident_rate = incident_count / total if total > 0 else 0.0

        composite = (
            success_rate * 0.4
            + calibration * 0.2
            + max(0, 1.0 - avg_latency / 10000) * 0.2
            + (1.0 - min(incident_rate, 1.0)) * 0.2
        )

        return FitnessScore(
            success_rate_7d=round(success_rate, 4),
            avg_confidence_calibration=round(calibration, 4),
            avg_latency_ms=round(avg_latency, 1),
            vigil_incident_rate=round(incident_rate, 4),
            composite_fitness=round(composite, 4),
        )

    async def compute_daily_snapshot(self, target_date: date) -> PerformanceSnapshot:
        day_start = datetime.combine(target_date, datetime.min.time())
        day_end = day_start + timedelta(days=1)

        traces = await self.episodic.get_traces(since=day_start, limit=1000)
        traces = [t for t in traces if t.timestamp < day_end]

        if not traces:
            return PerformanceSnapshot(date=target_date)

        total = len(traces)
        successes = sum(1 for t in traces if t.success)
        success_rate = successes / total
        avg_confidence = sum(t.confidence for t in traces) / total
        avg_latency = sum(t.latency_ms for t in traces) / total

        return PerformanceSnapshot(
            date=target_date,
            total_tasks=total,
            successful_tasks=successes,
            success_rate=round(success_rate, 4),
            avg_confidence=round(avg_confidence, 4),
            avg_latency_ms=round(avg_latency, 1),
            composite_fitness=round(success_rate * 0.6 + (1.0 - abs(avg_confidence - success_rate)) * 0.4, 4),
        )

    async def get_improvement_delta(self, day_a: date, day_b: date) -> dict:
        snap_a = await self.compute_daily_snapshot(day_a)
        snap_b = await self.compute_daily_snapshot(day_b)
        return {
            "day_a": snap_a.model_dump(),
            "day_b": snap_b.model_dump(),
            "success_rate_delta": round(snap_b.success_rate - snap_a.success_rate, 4),
            "fitness_delta": round(snap_b.composite_fitness - snap_a.composite_fitness, 4),
        }
