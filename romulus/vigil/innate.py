import re
import time
from collections import defaultdict
from pathlib import Path

import yaml

from romulus.models.actions import AgentAction
from romulus.models.vigil import ThreatCategory, VigilVerdict


class InnateLayer:
    def __init__(self, rules_path: str | None = None):
        if rules_path is None:
            rules_path = str(Path(__file__).parent / "innate_rules.yaml")

        with open(rules_path) as f:
            self._config = yaml.safe_load(f)

        self._destructive_patterns = []
        for entry in self._config.get("destructive_patterns", []):
            flags = re.IGNORECASE if entry.get("case_insensitive") else 0
            self._destructive_patterns.append({
                "pattern": re.compile(entry["pattern"], flags),
                "category": ThreatCategory(entry["category"]),
                "reason": entry["reason"],
            })

        self._scope_patterns = []
        for entry in self._config.get("scope_violations", []):
            self._scope_patterns.append({
                "pattern": re.compile(re.escape(entry["pattern"])),
                "category": ThreatCategory(entry["category"]),
                "reason": entry["reason"],
            })

        loop_cfg = self._config.get("loop_detection", {})
        self._max_identical = loop_cfg.get("max_identical_actions", 10)
        self._loop_window = loop_cfg.get("window_seconds", 60)
        self._action_history: dict[str, list[float]] = defaultdict(list)

    def check(self, action: AgentAction) -> VigilVerdict:
        start = time.monotonic()

        target = action.target
        params_str = str(action.parameters)
        full_text = f"{target} {params_str}"

        for rule in self._destructive_patterns:
            if rule["pattern"].search(full_text):
                elapsed = int((time.monotonic() - start) * 1_000_000) / 1000
                return VigilVerdict(
                    approved=False,
                    category=rule["category"],
                    layer="innate",
                    reason=rule["reason"],
                    latency_ms=max(1, int(elapsed)),
                )

        for rule in self._scope_patterns:
            if rule["pattern"].search(full_text):
                elapsed = int((time.monotonic() - start) * 1_000_000) / 1000
                return VigilVerdict(
                    approved=False,
                    category=rule["category"],
                    layer="innate",
                    reason=rule["reason"],
                    latency_ms=max(1, int(elapsed)),
                )

        loop_verdict = self._check_looping(action)
        if loop_verdict:
            return loop_verdict

        elapsed = int((time.monotonic() - start) * 1_000_000) / 1000
        return VigilVerdict(approved=True, layer="innate", latency_ms=max(1, int(elapsed)))

    def _check_looping(self, action: AgentAction) -> VigilVerdict | None:
        key = f"{action.action_type}:{action.target}"
        now = time.time()

        self._action_history[key] = [
            t for t in self._action_history[key]
            if now - t < self._loop_window
        ]
        self._action_history[key].append(now)

        if len(self._action_history[key]) >= self._max_identical:
            return VigilVerdict(
                approved=False,
                category=ThreatCategory.LOOPING,
                layer="innate",
                reason=f"Action repeated {len(self._action_history[key])} times in {self._loop_window}s",
                latency_ms=0,
            )
        return None
