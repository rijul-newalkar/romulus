"""Unit tests for all Romulus data models."""

from datetime import date, datetime
from uuid import UUID

import pytest

from romulus.models.actions import ActionOutcome, AgentAction
from romulus.models.arena import FitnessScore, PerformanceSnapshot
from romulus.models.dream import DreamReport
from romulus.models.episodic import EpisodicTrace, TaskResult
from romulus.models.identity import AgentIdentity
from romulus.models.semantic import SemanticRule
from romulus.models.vigil import ThreatCategory, VigilVerdict


# ---------------------------------------------------------------------------
# EpisodicTrace
# ---------------------------------------------------------------------------

class TestEpisodicTrace:
    def test_creation_minimal(self):
        trace = EpisodicTrace(
            task="test task",
            decision="respond",
            outcome="done",
            success=True,
            confidence=0.8,
        )
        assert trace.task == "test task"
        assert trace.decision == "respond"
        assert trace.outcome == "done"
        assert trace.success is True
        assert trace.confidence == 0.8

    def test_defaults(self):
        trace = EpisodicTrace(
            task="t", decision="d", outcome="o", success=False, confidence=0.5,
        )
        # id should be a valid UUID string
        UUID(trace.id)
        assert isinstance(trace.timestamp, datetime)
        assert trace.context == {}
        assert trace.tools_used == []
        assert trace.latency_ms == 0
        assert trace.tokens_used == 0
        assert trace.alternatives_considered == []

    def test_unique_ids(self):
        t1 = EpisodicTrace(task="a", decision="d", outcome="o", success=True, confidence=0.9)
        t2 = EpisodicTrace(task="b", decision="d", outcome="o", success=True, confidence=0.9)
        assert t1.id != t2.id

    def test_serialization_roundtrip(self):
        trace = EpisodicTrace(
            task="calculate pi",
            decision="use_tool",
            outcome="3.14159",
            success=True,
            confidence=0.95,
            tools_used=["calculate"],
            context={"source": "user"},
            latency_ms=150,
            tokens_used=42,
            alternatives_considered=["estimate", "lookup"],
        )
        data = trace.model_dump()
        restored = EpisodicTrace(**data)
        assert restored.task == trace.task
        assert restored.tools_used == ["calculate"]
        assert restored.alternatives_considered == ["estimate", "lookup"]
        assert restored.latency_ms == 150
        assert restored.tokens_used == 42

    def test_json_serialization(self):
        trace = EpisodicTrace(
            task="t", decision="d", outcome="o", success=True, confidence=0.5,
        )
        json_str = trace.model_dump_json()
        assert "task" in json_str
        assert "confidence" in json_str


# ---------------------------------------------------------------------------
# TaskResult
# ---------------------------------------------------------------------------

class TestTaskResult:
    def test_creation(self):
        result = TaskResult(
            task="hello", success=True, confidence=0.9, response="Hi there!",
        )
        assert result.task == "hello"
        assert result.success is True
        assert result.response == "Hi there!"

    def test_defaults(self):
        result = TaskResult(
            task="x", success=False, confidence=0.1, response="error",
        )
        assert result.vigil_flags == []
        assert result.tokens_used == 0
        assert result.latency_ms == 0

    def test_with_vigil_flags(self):
        result = TaskResult(
            task="rm -rf /", success=False, confidence=1.0,
            response="Blocked", vigil_flags=["Destructive command detected"],
        )
        assert len(result.vigil_flags) == 1
        assert "Destructive" in result.vigil_flags[0]

    def test_serialization_roundtrip(self):
        result = TaskResult(
            task="test", success=True, confidence=0.8,
            response="ok", vigil_flags=["a", "b"], tokens_used=100, latency_ms=50,
        )
        data = result.model_dump()
        restored = TaskResult(**data)
        assert restored == result


# ---------------------------------------------------------------------------
# SemanticRule
# ---------------------------------------------------------------------------

class TestSemanticRule:
    def test_creation(self):
        rule = SemanticRule(rule="When X, do Y", confidence=0.85)
        assert rule.rule == "When X, do Y"
        assert rule.confidence == 0.85

    def test_defaults(self):
        rule = SemanticRule(rule="test", confidence=0.7)
        UUID(rule.id)
        assert isinstance(rule.last_validated, datetime)
        assert rule.evidence_count == 1
        assert rule.contradictions == 0
        assert rule.domain == "general"
        assert rule.source_episode_ids == []

    def test_custom_domain(self):
        rule = SemanticRule(
            rule="When coding, use type hints",
            confidence=0.9,
            domain="coding",
            source_episode_ids=["ep1", "ep2"],
        )
        assert rule.domain == "coding"
        assert len(rule.source_episode_ids) == 2

    def test_serialization(self):
        rule = SemanticRule(
            rule="test rule", confidence=0.8,
            evidence_count=5, contradictions=1,
        )
        data = rule.model_dump()
        restored = SemanticRule(**data)
        assert restored.rule == "test rule"
        assert restored.evidence_count == 5
        assert restored.contradictions == 1


# ---------------------------------------------------------------------------
# AgentIdentity
# ---------------------------------------------------------------------------

class TestAgentIdentity:
    def test_creation(self):
        identity = AgentIdentity(name="Romulus")
        assert identity.name == "Romulus"

    def test_defaults(self):
        identity = AgentIdentity(name="Test")
        UUID(identity.id)
        assert identity.version == "0.1.0"
        assert isinstance(identity.created_at, datetime)
        assert identity.soul_spec == ""
        assert identity.total_tasks == 0
        assert identity.successful_tasks == 0
        assert identity.trust_score == 0.5
        assert identity.total_uptime_seconds == 0

    def test_custom_values(self):
        identity = AgentIdentity(
            name="Custom",
            version="1.0.0",
            soul_spec="Be helpful.",
            total_tasks=100,
            successful_tasks=90,
            trust_score=0.95,
            total_uptime_seconds=86400,
        )
        assert identity.total_tasks == 100
        assert identity.trust_score == 0.95

    def test_serialization(self):
        identity = AgentIdentity(name="Test", soul_spec="spec")
        data = identity.model_dump()
        assert data["name"] == "Test"
        assert data["soul_spec"] == "spec"


# ---------------------------------------------------------------------------
# DreamReport
# ---------------------------------------------------------------------------

class TestDreamReport:
    def test_creation_empty(self):
        report = DreamReport()
        UUID(report.id)
        assert isinstance(report.date, datetime)
        assert report.episodes_processed == 0
        assert report.counterfactuals_run == 0
        assert report.new_rules_extracted == []
        assert report.rules_invalidated == []
        assert report.memories_pruned == 0
        assert report.weak_spots_found == []
        assert report.confidence_adjustment == 0.0
        assert report.summary == ""

    def test_with_data(self):
        rule = SemanticRule(rule="test rule", confidence=0.8)
        report = DreamReport(
            episodes_processed=10,
            counterfactuals_run=3,
            new_rules_extracted=[rule],
            rules_invalidated=["old-id"],
            memories_pruned=5,
            weak_spots_found=["low confidence tasks"],
            confidence_adjustment=0.05,
            summary="Productive dream cycle",
        )
        assert report.episodes_processed == 10
        assert len(report.new_rules_extracted) == 1
        assert report.new_rules_extracted[0].rule == "test rule"
        assert report.memories_pruned == 5
        assert report.summary == "Productive dream cycle"

    def test_serialization(self):
        report = DreamReport(
            episodes_processed=5,
            summary="A brief dream",
        )
        data = report.model_dump()
        assert data["episodes_processed"] == 5


# ---------------------------------------------------------------------------
# VigilVerdict and ThreatCategory
# ---------------------------------------------------------------------------

class TestThreatCategory:
    def test_all_values(self):
        expected = {
            "destructive", "looping", "hallucination",
            "scope_escape", "cost_runaway", "confidence_anomaly", "cascade_risk",
        }
        actual = {member.value for member in ThreatCategory}
        assert actual == expected

    def test_enum_string(self):
        assert ThreatCategory.DESTRUCTIVE == "destructive"
        assert ThreatCategory.LOOPING == "looping"
        assert ThreatCategory.SCOPE_ESCAPE == "scope_escape"

    def test_from_value(self):
        cat = ThreatCategory("destructive")
        assert cat == ThreatCategory.DESTRUCTIVE


class TestVigilVerdict:
    def test_approved(self):
        verdict = VigilVerdict(approved=True)
        assert verdict.approved is True
        assert verdict.category is None
        assert verdict.layer == ""
        assert verdict.reason == ""

    def test_denied(self):
        verdict = VigilVerdict(
            approved=False,
            category=ThreatCategory.DESTRUCTIVE,
            layer="innate",
            reason="Dangerous command",
            latency_ms=5,
        )
        assert verdict.approved is False
        assert verdict.category == ThreatCategory.DESTRUCTIVE
        assert verdict.layer == "innate"
        assert verdict.latency_ms == 5

    def test_serialization(self):
        verdict = VigilVerdict(
            approved=False,
            category=ThreatCategory.LOOPING,
            layer="innate",
            reason="Loop detected",
        )
        data = verdict.model_dump()
        assert data["category"] == "looping"
        assert data["approved"] is False


# ---------------------------------------------------------------------------
# AgentAction and ActionOutcome
# ---------------------------------------------------------------------------

class TestAgentAction:
    def test_creation(self):
        action = AgentAction(action_type="tool_call", target="calculate")
        assert action.action_type == "tool_call"
        assert action.target == "calculate"

    def test_defaults(self):
        action = AgentAction(action_type="a", target="b")
        assert action.parameters == {}
        assert action.reversible is True

    def test_with_params(self):
        action = AgentAction(
            action_type="tool_call",
            target="calculate",
            parameters={"expression": "2+2"},
            reversible=False,
        )
        assert action.parameters["expression"] == "2+2"
        assert action.reversible is False


class TestActionOutcome:
    def test_executed(self):
        action = AgentAction(action_type="tool_call", target="get_time")
        verdict = VigilVerdict(approved=True, layer="all_clear")
        outcome = ActionOutcome(
            action=action, verdict=verdict, executed=True, result="2024-01-01",
        )
        assert outcome.executed is True
        assert outcome.result == "2024-01-01"
        assert outcome.error == ""

    def test_blocked(self):
        action = AgentAction(action_type="tool_call", target="rm -rf /")
        verdict = VigilVerdict(
            approved=False, category=ThreatCategory.DESTRUCTIVE,
            layer="innate", reason="dangerous",
        )
        outcome = ActionOutcome(
            action=action, verdict=verdict, executed=False, error="blocked",
        )
        assert outcome.executed is False
        assert outcome.error == "blocked"

    def test_serialization(self):
        action = AgentAction(action_type="a", target="b")
        verdict = VigilVerdict(approved=True)
        outcome = ActionOutcome(action=action, verdict=verdict, executed=True, result="ok")
        data = outcome.model_dump()
        assert data["executed"] is True
        assert data["action"]["target"] == "b"


# ---------------------------------------------------------------------------
# FitnessScore and PerformanceSnapshot
# ---------------------------------------------------------------------------

class TestFitnessScore:
    def test_defaults(self):
        score = FitnessScore()
        assert score.agent_id == ""
        assert isinstance(score.timestamp, datetime)
        assert score.success_rate_7d == 0.0
        assert score.avg_confidence_calibration == 0.0
        assert score.avg_latency_ms == 0.0
        assert score.vigil_incident_rate == 0.0
        assert score.composite_fitness == 0.0

    def test_custom(self):
        score = FitnessScore(
            agent_id="agent-1",
            success_rate_7d=0.85,
            avg_confidence_calibration=0.9,
            avg_latency_ms=200.5,
            vigil_incident_rate=0.05,
            composite_fitness=0.82,
        )
        assert score.success_rate_7d == 0.85
        assert score.composite_fitness == 0.82

    def test_serialization(self):
        score = FitnessScore(success_rate_7d=0.7, composite_fitness=0.65)
        data = score.model_dump()
        assert data["success_rate_7d"] == 0.7


class TestPerformanceSnapshot:
    def test_creation(self):
        snap = PerformanceSnapshot(date=date(2024, 1, 15))
        assert snap.date == date(2024, 1, 15)

    def test_defaults(self):
        snap = PerformanceSnapshot(date=date.today())
        assert snap.total_tasks == 0
        assert snap.successful_tasks == 0
        assert snap.success_rate == 0.0
        assert snap.avg_confidence == 0.0
        assert snap.avg_latency_ms == 0.0
        assert snap.vigil_incidents == 0
        assert snap.composite_fitness == 0.0

    def test_with_data(self):
        snap = PerformanceSnapshot(
            date=date(2024, 1, 15),
            total_tasks=20,
            successful_tasks=18,
            success_rate=0.9,
            avg_confidence=0.85,
            avg_latency_ms=300.0,
            vigil_incidents=2,
            composite_fitness=0.88,
        )
        assert snap.total_tasks == 20
        assert snap.successful_tasks == 18
        assert snap.composite_fitness == 0.88

    def test_serialization(self):
        snap = PerformanceSnapshot(date=date(2024, 6, 1), total_tasks=10)
        data = snap.model_dump()
        assert data["total_tasks"] == 10
