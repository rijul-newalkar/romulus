"""Tests for the Chronicle memory system (database, episodic, semantic, identity stores)."""

from datetime import datetime, timedelta

import pytest

from romulus.chronicle.database import ChronicleDB
from romulus.chronicle.episodic import EpisodicStore
from romulus.chronicle.identity import IdentityStore
from romulus.chronicle.semantic import SemanticStore
from romulus.models.episodic import EpisodicTrace
from romulus.models.semantic import SemanticRule


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
async def db(tmp_path):
    """Create a file-backed ChronicleDB and initialize schema."""
    db_path = str(tmp_path / "test_chronicle.db")
    chronicle = ChronicleDB(db_path=db_path)
    await chronicle.initialize()
    return chronicle


@pytest.fixture
async def episodic_store(db):
    return EpisodicStore(db)


@pytest.fixture
async def semantic_store(db):
    return SemanticStore(db)


@pytest.fixture
async def identity_store(db):
    return IdentityStore(db)


def make_trace(
    task: str = "test task",
    success: bool = True,
    confidence: float = 0.8,
    timestamp: datetime | None = None,
    latency_ms: int = 100,
    tokens_used: int = 50,
) -> EpisodicTrace:
    """Helper to create a trace with sensible defaults."""
    return EpisodicTrace(
        task=task,
        decision="respond",
        outcome="done" if success else "failed",
        success=success,
        confidence=confidence,
        timestamp=timestamp or datetime.utcnow(),
        latency_ms=latency_ms,
        tokens_used=tokens_used,
    )


# ---------------------------------------------------------------------------
# ChronicleDB initialization
# ---------------------------------------------------------------------------

class TestChronicleDB:
    async def test_initialize_creates_tables(self, db):
        """Tables should exist after initialization."""
        tables = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        table_names = {row["name"] for row in tables}
        assert "episodic_traces" in table_names
        assert "semantic_rules" in table_names
        assert "agent_identity" in table_names
        assert "dream_reports" in table_names
        assert "vigil_incidents" in table_names

    async def test_initialize_creates_indexes(self, db):
        indexes = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
        )
        index_names = {row["name"] for row in indexes}
        assert "idx_traces_timestamp" in index_names
        assert "idx_traces_success" in index_names
        assert "idx_rules_domain" in index_names
        assert "idx_vigil_timestamp" in index_names

    async def test_double_initialize_is_safe(self, db):
        """Calling initialize twice should not raise."""
        await db.initialize()
        tables = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        assert len(tables) >= 5

    async def test_execute_returns_list_of_dicts(self, db):
        result = await db.execute("SELECT 1 as val")
        assert isinstance(result, list)
        assert result[0]["val"] == 1

    async def test_execute_insert(self, db):
        row_id = await db.execute_insert(
            "INSERT INTO semantic_rules (id, rule, confidence, last_validated) VALUES (?, ?, ?, ?)",
            ("test-id", "test rule", 0.8, datetime.utcnow().isoformat()),
        )
        assert row_id == "test-id"


# ---------------------------------------------------------------------------
# EpisodicStore
# ---------------------------------------------------------------------------

class TestEpisodicStore:
    async def test_log_and_get_trace(self, episodic_store):
        trace = make_trace(task="hello world")
        trace_id = await episodic_store.log_trace(trace)
        assert trace_id == trace.id

        traces = await episodic_store.get_traces()
        assert len(traces) == 1
        assert traces[0].task == "hello world"
        assert traces[0].id == trace_id

    async def test_log_multiple_traces(self, episodic_store):
        for i in range(5):
            await episodic_store.log_trace(make_trace(task=f"task {i}"))

        traces = await episodic_store.get_traces()
        assert len(traces) == 5

    async def test_get_traces_with_limit(self, episodic_store):
        for i in range(10):
            await episodic_store.log_trace(make_trace(task=f"task {i}"))

        traces = await episodic_store.get_traces(limit=3)
        assert len(traces) == 3

    async def test_get_traces_since(self, episodic_store):
        old_trace = make_trace(
            task="old", timestamp=datetime.utcnow() - timedelta(hours=48),
        )
        new_trace = make_trace(
            task="new", timestamp=datetime.utcnow(),
        )
        await episodic_store.log_trace(old_trace)
        await episodic_store.log_trace(new_trace)

        since = datetime.utcnow() - timedelta(hours=24)
        traces = await episodic_store.get_traces(since=since)
        assert len(traces) == 1
        assert traces[0].task == "new"

    async def test_get_traces_filter_success(self, episodic_store):
        await episodic_store.log_trace(make_trace(task="good", success=True))
        await episodic_store.log_trace(make_trace(task="bad", success=False))

        successes = await episodic_store.get_traces(success=True)
        failures = await episodic_store.get_traces(success=False)

        assert len(successes) == 1
        assert successes[0].task == "good"
        assert len(failures) == 1
        assert failures[0].task == "bad"

    async def test_get_traces_for_dream(self, episodic_store):
        # Trace within 24 hours should be returned
        recent = make_trace(task="recent", timestamp=datetime.utcnow() - timedelta(hours=2))
        await episodic_store.log_trace(recent)

        # Trace older than 24 hours should not be returned
        old = make_trace(task="old", timestamp=datetime.utcnow() - timedelta(hours=48))
        await episodic_store.log_trace(old)

        dream_traces = await episodic_store.get_traces_for_dream(hours=24)
        tasks = [t.task for t in dream_traces]
        assert "recent" in tasks
        assert "old" not in tasks

    async def test_count_traces(self, episodic_store):
        assert await episodic_store.count_traces() == 0

        for i in range(3):
            await episodic_store.log_trace(make_trace(task=f"t{i}"))

        assert await episodic_store.count_traces() == 3

    async def test_count_traces_since(self, episodic_store):
        old = make_trace(task="old", timestamp=datetime.utcnow() - timedelta(days=10))
        new = make_trace(task="new", timestamp=datetime.utcnow())
        await episodic_store.log_trace(old)
        await episodic_store.log_trace(new)

        since = datetime.utcnow() - timedelta(days=5)
        assert await episodic_store.count_traces(since=since) == 1

    async def test_delete_old_traces_keeps_failures(self, episodic_store):
        old_success = make_trace(
            task="old success", success=True,
            timestamp=datetime.utcnow() - timedelta(days=20),
        )
        old_failure = make_trace(
            task="old failure", success=False,
            timestamp=datetime.utcnow() - timedelta(days=20),
        )
        recent = make_trace(task="recent", timestamp=datetime.utcnow())

        await episodic_store.log_trace(old_success)
        await episodic_store.log_trace(old_failure)
        await episodic_store.log_trace(recent)

        deleted = await episodic_store.delete_old_traces(older_than_days=14, keep_failures=True)
        assert deleted == 1  # Only the old success should be deleted

        remaining = await episodic_store.get_traces(limit=100)
        tasks = {t.task for t in remaining}
        assert "old failure" in tasks
        assert "recent" in tasks
        assert "old success" not in tasks

    async def test_delete_old_traces_all(self, episodic_store):
        old_success = make_trace(
            task="old success", success=True,
            timestamp=datetime.utcnow() - timedelta(days=20),
        )
        old_failure = make_trace(
            task="old failure", success=False,
            timestamp=datetime.utcnow() - timedelta(days=20),
        )
        await episodic_store.log_trace(old_success)
        await episodic_store.log_trace(old_failure)

        deleted = await episodic_store.delete_old_traces(older_than_days=14, keep_failures=False)
        assert deleted == 2

    async def test_trace_preserves_all_fields(self, episodic_store):
        trace = EpisodicTrace(
            task="complex task",
            decision="use_tool",
            outcome="success",
            success=True,
            confidence=0.95,
            tools_used=["calculate", "get_time"],
            context={"key": "value", "nested": {"a": 1}},
            latency_ms=250,
            tokens_used=128,
            alternatives_considered=["approach_a", "approach_b"],
        )
        await episodic_store.log_trace(trace)

        traces = await episodic_store.get_traces()
        restored = traces[0]
        assert restored.tools_used == ["calculate", "get_time"]
        assert restored.context == {"key": "value", "nested": {"a": 1}}
        assert restored.alternatives_considered == ["approach_a", "approach_b"]
        assert restored.latency_ms == 250
        assert restored.tokens_used == 128


# ---------------------------------------------------------------------------
# SemanticStore
# ---------------------------------------------------------------------------

class TestSemanticStore:
    async def test_add_and_get_rule(self, semantic_store):
        rule = SemanticRule(rule="When X, do Y", confidence=0.85)
        rule_id = await semantic_store.add_rule(rule)
        assert rule_id == rule.id

        rules = await semantic_store.get_all_rules()
        assert len(rules) == 1
        assert rules[0].rule == "When X, do Y"
        assert rules[0].confidence == 0.85

    async def test_get_rule_by_id(self, semantic_store):
        rule = SemanticRule(rule="test", confidence=0.7)
        await semantic_store.add_rule(rule)

        retrieved = await semantic_store.get_rule(rule.id)
        assert retrieved is not None
        assert retrieved.rule == "test"

    async def test_get_rule_not_found(self, semantic_store):
        retrieved = await semantic_store.get_rule("nonexistent-id")
        assert retrieved is None

    async def test_get_all_rules_ordered_by_confidence(self, semantic_store):
        await semantic_store.add_rule(SemanticRule(rule="low", confidence=0.5))
        await semantic_store.add_rule(SemanticRule(rule="high", confidence=0.95))
        await semantic_store.add_rule(SemanticRule(rule="mid", confidence=0.75))

        rules = await semantic_store.get_all_rules()
        confidences = [r.confidence for r in rules]
        assert confidences == sorted(confidences, reverse=True)

    async def test_get_rules_by_domain(self, semantic_store):
        await semantic_store.add_rule(
            SemanticRule(rule="coding rule", confidence=0.8, domain="coding")
        )
        await semantic_store.add_rule(
            SemanticRule(rule="general rule", confidence=0.7, domain="general")
        )

        coding_rules = await semantic_store.get_all_rules(domain="coding")
        assert len(coding_rules) == 1
        assert coding_rules[0].domain == "coding"

        general_rules = await semantic_store.get_all_rules(domain="general")
        assert len(general_rules) == 1

    async def test_validate_rule(self, semantic_store):
        rule = SemanticRule(rule="test", confidence=0.7, evidence_count=1)
        await semantic_store.add_rule(rule)

        await semantic_store.validate_rule(rule.id)

        updated = await semantic_store.get_rule(rule.id)
        assert updated is not None
        assert updated.evidence_count == 2

    async def test_validate_rule_multiple_times(self, semantic_store):
        rule = SemanticRule(rule="test", confidence=0.7, evidence_count=1)
        await semantic_store.add_rule(rule)

        for _ in range(5):
            await semantic_store.validate_rule(rule.id)

        updated = await semantic_store.get_rule(rule.id)
        assert updated is not None
        assert updated.evidence_count == 6

    async def test_invalidate_rule_increments_contradictions(self, semantic_store):
        rule = SemanticRule(rule="test", confidence=0.7, evidence_count=5)
        await semantic_store.add_rule(rule)

        await semantic_store.invalidate_rule(rule.id)

        updated = await semantic_store.get_rule(rule.id)
        assert updated is not None
        assert updated.contradictions == 1

    async def test_invalidate_rule_auto_deletes(self, semantic_store):
        """Rule should be deleted when contradictions exceed evidence_count."""
        rule = SemanticRule(rule="weak rule", confidence=0.6, evidence_count=1)
        await semantic_store.add_rule(rule)

        # First invalidation: contradictions=1, evidence=1 (not deleted, need > not >=)
        await semantic_store.invalidate_rule(rule.id)
        still_there = await semantic_store.get_rule(rule.id)
        # At contradictions=1, evidence=1, contradictions is NOT > evidence, so rule stays
        assert still_there is not None

        # Second invalidation: contradictions=2 > evidence=1 -> should delete
        await semantic_store.invalidate_rule(rule.id)
        gone = await semantic_store.get_rule(rule.id)
        assert gone is None

    async def test_invalidate_rule_deletion_threshold(self, semantic_store):
        """With evidence_count=3, need 4 contradictions to trigger deletion."""
        rule = SemanticRule(rule="robust rule", confidence=0.8, evidence_count=3)
        await semantic_store.add_rule(rule)

        # 3 invalidations -> contradictions == evidence_count (not deleted yet)
        for _ in range(3):
            await semantic_store.invalidate_rule(rule.id)
        assert await semantic_store.get_rule(rule.id) is not None

        # 4th invalidation -> contradictions > evidence_count (deleted)
        await semantic_store.invalidate_rule(rule.id)
        assert await semantic_store.get_rule(rule.id) is None

    async def test_count_rules(self, semantic_store):
        assert await semantic_store.count_rules() == 0

        await semantic_store.add_rule(SemanticRule(rule="r1", confidence=0.7))
        await semantic_store.add_rule(SemanticRule(rule="r2", confidence=0.8))

        assert await semantic_store.count_rules() == 2

    async def test_rule_preserves_source_episode_ids(self, semantic_store):
        rule = SemanticRule(
            rule="test", confidence=0.7,
            source_episode_ids=["ep-1", "ep-2", "ep-3"],
        )
        await semantic_store.add_rule(rule)

        retrieved = await semantic_store.get_rule(rule.id)
        assert retrieved is not None
        assert retrieved.source_episode_ids == ["ep-1", "ep-2", "ep-3"]


# ---------------------------------------------------------------------------
# IdentityStore
# ---------------------------------------------------------------------------

class TestIdentityStore:
    async def test_create_identity(self, identity_store):
        identity = await identity_store.get_or_create_identity("Romulus")
        assert identity.name == "Romulus"
        assert identity.total_tasks == 0
        assert identity.trust_score == 0.5

    async def test_get_or_create_returns_existing(self, identity_store):
        first = await identity_store.get_or_create_identity("Romulus", "soul spec v1")
        second = await identity_store.get_or_create_identity("Different Name", "soul spec v2")
        # Should return the existing identity, not create a new one
        assert first.id == second.id
        assert second.name == "Romulus"  # Name from first creation

    async def test_get_identity(self, identity_store):
        # No identity yet
        assert await identity_store.get_identity() is None

        await identity_store.get_or_create_identity("Test")
        identity = await identity_store.get_identity()
        assert identity is not None
        assert identity.name == "Test"

    async def test_update_stats_success(self, identity_store):
        await identity_store.get_or_create_identity("Test")

        await identity_store.update_stats(task_success=True)

        identity = await identity_store.get_identity()
        assert identity.total_tasks == 1
        assert identity.successful_tasks == 1

    async def test_update_stats_failure(self, identity_store):
        await identity_store.get_or_create_identity("Test")

        await identity_store.update_stats(task_success=False)

        identity = await identity_store.get_identity()
        assert identity.total_tasks == 1
        assert identity.successful_tasks == 0

    async def test_update_stats_mixed(self, identity_store):
        await identity_store.get_or_create_identity("Test")

        for _ in range(7):
            await identity_store.update_stats(task_success=True)
        for _ in range(3):
            await identity_store.update_stats(task_success=False)

        identity = await identity_store.get_identity()
        assert identity.total_tasks == 10
        assert identity.successful_tasks == 7

    async def test_trust_score_recalculation(self, identity_store):
        """Trust starts at 0.5 and adjusts based on success rate, dampened by sample size."""
        await identity_store.get_or_create_identity("Test")

        # All successes should push trust above 0.5
        for _ in range(10):
            await identity_store.update_stats(task_success=True)

        identity = await identity_store.get_identity()
        assert identity.trust_score > 0.5

    async def test_trust_score_decreases_on_failures(self, identity_store):
        await identity_store.get_or_create_identity("Test")

        # All failures should push trust below 0.5
        for _ in range(10):
            await identity_store.update_stats(task_success=False)

        identity = await identity_store.get_identity()
        assert identity.trust_score < 0.5

    async def test_trust_score_formula(self, identity_store):
        """
        Trust formula: 0.5 + (success_rate - 0.5) * min(total_tasks / 50, 1.0)
        With 50 tasks at 100% success -> trust = 0.5 + (1.0 - 0.5) * 1.0 = 1.0
        """
        await identity_store.get_or_create_identity("Test")

        for _ in range(50):
            await identity_store.update_stats(task_success=True)

        identity = await identity_store.get_identity()
        # With 50 tasks, 100% success: trust = 0.5 + 0.5 * 1.0 = 1.0
        assert identity.trust_score == 1.0

    async def test_trust_score_dampened_early(self, identity_store):
        """
        With only a few tasks, trust doesn't swing as much.
        After 10 tasks at 100% success:
            trust = 0.5 + (1.0 - 0.5) * min(10/50, 1.0) = 0.5 + 0.5 * 0.2 = 0.6
        """
        await identity_store.get_or_create_identity("Test")

        for _ in range(10):
            await identity_store.update_stats(task_success=True)

        identity = await identity_store.get_identity()
        assert identity.trust_score == 0.6

    async def test_identity_preserves_soul_spec(self, identity_store):
        await identity_store.get_or_create_identity("Test", soul_spec="Be helpful and kind.")
        identity = await identity_store.get_identity()
        assert identity.soul_spec == "Be helpful and kind."
