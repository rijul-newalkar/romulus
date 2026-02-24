"""Tests for the Arena fitness monitoring system."""

import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from romulus.arena.monitor import FitnessMonitor
from romulus.chronicle.database import ChronicleDB
from romulus.chronicle.episodic import EpisodicStore
from romulus.models.actions import AgentAction
from romulus.models.episodic import EpisodicTrace
from romulus.models.vigil import ThreatCategory, VigilVerdict
from romulus.vigil.incidents import IncidentLogger


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
async def db(tmp_path):
    db_path = str(tmp_path / "test_arena.db")
    chronicle = ChronicleDB(db_path=db_path)
    await chronicle.initialize()
    return chronicle


@pytest.fixture
async def episodic_store(db):
    return EpisodicStore(db)


@pytest.fixture
async def incident_logger(db):
    return IncidentLogger(db)


@pytest.fixture
async def monitor(episodic_store, incident_logger):
    return FitnessMonitor(episodic_store, incident_logger)


def make_trace(
    task: str = "test",
    success: bool = True,
    confidence: float = 0.8,
    latency_ms: int = 100,
    timestamp: datetime | None = None,
) -> EpisodicTrace:
    return EpisodicTrace(
        task=task,
        decision="respond",
        outcome="done" if success else "failed",
        success=success,
        confidence=confidence,
        latency_ms=latency_ms,
        tokens_used=50,
        timestamp=timestamp or datetime.utcnow(),
    )


async def seed_traces(
    store: EpisodicStore,
    count: int,
    success_rate: float = 0.8,
    confidence: float = 0.8,
    latency_ms: int = 200,
    base_time: datetime | None = None,
):
    """Seed the store with a known distribution of traces."""
    base = base_time or datetime.utcnow()
    success_count = int(count * success_rate)

    for i in range(count):
        is_success = i < success_count
        trace = make_trace(
            task=f"task-{i}",
            success=is_success,
            confidence=confidence,
            latency_ms=latency_ms,
            timestamp=base - timedelta(minutes=i),
        )
        await store.log_trace(trace)


# ---------------------------------------------------------------------------
# FitnessMonitor.compute_fitness
# ---------------------------------------------------------------------------

class TestComputeFitness:
    async def test_empty_returns_default(self, monitor):
        """No traces should return a default FitnessScore with all zeros."""
        fitness = await monitor.compute_fitness()
        assert fitness.success_rate_7d == 0.0
        assert fitness.composite_fitness == 0.0
        assert fitness.avg_latency_ms == 0.0
        assert fitness.vigil_incident_rate == 0.0

    async def test_all_successes(self, monitor, episodic_store):
        await seed_traces(episodic_store, count=10, success_rate=1.0, confidence=1.0)

        fitness = await monitor.compute_fitness(window_days=7)
        assert fitness.success_rate_7d == 1.0

    async def test_all_failures(self, monitor, episodic_store):
        await seed_traces(episodic_store, count=10, success_rate=0.0, confidence=0.0)

        fitness = await monitor.compute_fitness(window_days=7)
        assert fitness.success_rate_7d == 0.0

    async def test_mixed_success_rate(self, monitor, episodic_store):
        # 8 successes out of 10 = 80%
        await seed_traces(episodic_store, count=10, success_rate=0.8)

        fitness = await monitor.compute_fitness(window_days=7)
        assert fitness.success_rate_7d == 0.8

    async def test_correct_confidence_calibration(self, monitor, episodic_store):
        """
        Calibration = 1.0 - abs(avg_confidence - actual_success_rate)
        If confidence=0.8 and success_rate=0.8 -> calibration=1.0
        """
        await seed_traces(
            episodic_store, count=10, success_rate=0.8, confidence=0.8,
        )
        fitness = await monitor.compute_fitness()
        assert fitness.avg_confidence_calibration == 1.0

    async def test_poor_calibration(self, monitor, episodic_store):
        """
        If confidence=0.9 and success_rate=0.5 -> calibration = 1.0 - 0.4 = 0.6
        """
        await seed_traces(
            episodic_store, count=10, success_rate=0.5, confidence=0.9,
        )
        fitness = await monitor.compute_fitness()
        assert fitness.avg_confidence_calibration == 0.6

    async def test_avg_latency(self, monitor, episodic_store):
        await seed_traces(episodic_store, count=10, latency_ms=500)
        fitness = await monitor.compute_fitness()
        assert fitness.avg_latency_ms == 500.0

    async def test_vigil_incident_rate(self, monitor, episodic_store, incident_logger):
        await seed_traces(episodic_store, count=10)

        # Log 2 incidents
        act = AgentAction(action_type="shell", target="bad_cmd")
        verdict = VigilVerdict(
            approved=False, category=ThreatCategory.DESTRUCTIVE,
            layer="innate", reason="test",
        )
        await incident_logger.log(act, verdict)
        await incident_logger.log(act, verdict)

        fitness = await monitor.compute_fitness(window_days=7)
        # 2 incidents / 10 traces = 0.2
        assert fitness.vigil_incident_rate == 0.2

    async def test_composite_fitness_formula(self, monitor, episodic_store):
        """
        composite = success_rate * 0.4
                   + calibration * 0.2
                   + max(0, 1.0 - avg_latency/10000) * 0.2
                   + (1.0 - min(incident_rate, 1.0)) * 0.2

        With success=1.0, confidence=1.0, latency=0, incidents=0:
            composite = 1.0*0.4 + 1.0*0.2 + 1.0*0.2 + 1.0*0.2 = 1.0
        """
        await seed_traces(
            episodic_store, count=10,
            success_rate=1.0, confidence=1.0, latency_ms=0,
        )
        fitness = await monitor.compute_fitness()
        assert fitness.composite_fitness == 1.0

    async def test_composite_accounts_for_latency(self, monitor, episodic_store):
        """High latency should reduce the composite score."""
        await seed_traces(
            episodic_store, count=10,
            success_rate=1.0, confidence=1.0, latency_ms=5000,
        )
        fitness = await monitor.compute_fitness()
        # latency component = max(0, 1.0 - 5000/10000) * 0.2 = 0.5 * 0.2 = 0.1
        # composite = 0.4 + 0.2 + 0.1 + 0.2 = 0.9
        assert fitness.composite_fitness == 0.9

    async def test_window_excludes_old_traces(self, monitor, episodic_store):
        """Traces older than the window should not be counted."""
        old_time = datetime.utcnow() - timedelta(days=30)
        await seed_traces(
            episodic_store, count=5,
            success_rate=0.0, base_time=old_time,
        )
        # Recent traces
        await seed_traces(
            episodic_store, count=5,
            success_rate=1.0,
        )

        fitness = await monitor.compute_fitness(window_days=7)
        assert fitness.success_rate_7d == 1.0


# ---------------------------------------------------------------------------
# FitnessMonitor.compute_daily_snapshot
# ---------------------------------------------------------------------------

class TestDailySnapshot:
    async def test_empty_day(self, monitor):
        snap = await monitor.compute_daily_snapshot(date.today())
        assert snap.total_tasks == 0
        assert snap.composite_fitness == 0.0

    async def test_snapshot_for_specific_day(self, monitor, episodic_store):
        # Use a fixed date in the past to avoid UTC/local timezone mismatch
        target = date.today() - timedelta(days=1)
        day_start = datetime.combine(target, datetime.min.time())

        # Add traces within that specific day
        for i in range(5):
            trace = make_trace(
                task=f"day-{i}",
                success=True,
                confidence=0.8,
                timestamp=day_start + timedelta(hours=i + 1),
            )
            await episodic_store.log_trace(trace)

        snap = await monitor.compute_daily_snapshot(target)
        assert snap.total_tasks == 5
        assert snap.successful_tasks == 5
        assert snap.success_rate == 1.0
        assert snap.date == target

    async def test_snapshot_success_rate(self, monitor, episodic_store):
        target = date.today() - timedelta(days=1)
        day_start = datetime.combine(target, datetime.min.time())
        # 3 successes, 2 failures
        for i in range(3):
            await episodic_store.log_trace(
                make_trace(success=True, timestamp=day_start + timedelta(hours=i + 1))
            )
        for i in range(2):
            await episodic_store.log_trace(
                make_trace(success=False, timestamp=day_start + timedelta(hours=i + 5))
            )

        snap = await monitor.compute_daily_snapshot(target)
        assert snap.total_tasks == 5
        assert snap.successful_tasks == 3
        assert snap.success_rate == 0.6

    async def test_snapshot_excludes_other_days(self, monitor, episodic_store):
        day_a = date.today() - timedelta(days=3)
        day_b = date.today() - timedelta(days=2)
        day_a_start = datetime.combine(day_a, datetime.min.time())
        day_b_start = datetime.combine(day_b, datetime.min.time())

        await episodic_store.log_trace(make_trace(task="day_a", timestamp=day_a_start + timedelta(hours=6)))
        await episodic_store.log_trace(make_trace(task="day_b", timestamp=day_b_start + timedelta(hours=6)))

        snap = await monitor.compute_daily_snapshot(day_b)
        assert snap.total_tasks == 1


# ---------------------------------------------------------------------------
# FitnessMonitor.get_improvement_delta
# ---------------------------------------------------------------------------

class TestImprovementDelta:
    async def test_improvement_delta(self, monitor, episodic_store):
        """Day B should show improvement over Day A."""
        day_a = date.today() - timedelta(days=2)
        day_b = date.today() - timedelta(days=1)

        # Day A: 50% success rate
        day_a_start = datetime.combine(day_a, datetime.min.time())
        for i in range(4):
            await episodic_store.log_trace(
                make_trace(
                    task=f"a-{i}",
                    success=(i < 2),
                    confidence=0.5,
                    timestamp=day_a_start + timedelta(hours=i),
                )
            )

        # Day B: 100% success rate
        day_b_start = datetime.combine(day_b, datetime.min.time())
        for i in range(4):
            await episodic_store.log_trace(
                make_trace(
                    task=f"b-{i}",
                    success=True,
                    confidence=0.9,
                    timestamp=day_b_start + timedelta(hours=i),
                )
            )

        delta = await monitor.get_improvement_delta(day_a, day_b)
        assert delta["success_rate_delta"] == 0.5  # 1.0 - 0.5
        assert delta["fitness_delta"] > 0

    async def test_no_change_delta(self, monitor, episodic_store):
        """Same performance on both days should give zero delta."""
        day_a = date.today() - timedelta(days=2)
        day_b = date.today() - timedelta(days=1)

        for target_date in [day_a, day_b]:
            start = datetime.combine(target_date, datetime.min.time())
            for i in range(4):
                await episodic_store.log_trace(
                    make_trace(
                        success=True,
                        confidence=0.8,
                        latency_ms=200,
                        timestamp=start + timedelta(hours=i),
                    )
                )

        delta = await monitor.get_improvement_delta(day_a, day_b)
        assert delta["success_rate_delta"] == 0.0
        assert delta["fitness_delta"] == 0.0

    async def test_delta_structure(self, monitor):
        day_a = date.today() - timedelta(days=2)
        day_b = date.today() - timedelta(days=1)
        delta = await monitor.get_improvement_delta(day_a, day_b)

        assert "day_a" in delta
        assert "day_b" in delta
        assert "success_rate_delta" in delta
        assert "fitness_delta" in delta
        assert "date" in delta["day_a"]
        assert "total_tasks" in delta["day_a"]
