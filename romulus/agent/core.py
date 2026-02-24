import json
import re
import time
from datetime import datetime
from typing import Any, Callable

from romulus.chronicle.episodic import EpisodicStore
from romulus.chronicle.identity import IdentityStore
from romulus.chronicle.semantic import SemanticStore
from romulus.llm.client import OllamaClient
from romulus.llm.prompts import AGENT_SYSTEM_PROMPT
from romulus.models.actions import ActionOutcome, AgentAction
from romulus.models.episodic import EpisodicTrace, TaskResult
from romulus.models.vigil import VigilVerdict
from romulus.vigil.sentinel import Sentinel


class ParsedResponse:
    def __init__(self, thought: str = "", action: str = "respond", params: dict = None,
                 response: str = "", confidence: float = 0.5, alternatives: list = None):
        self.thought = thought
        self.action = action
        self.params = params or {}
        self.response = response
        self.confidence = confidence
        self.alternatives = alternatives or []


class AgentCore:
    def __init__(
        self,
        llm: OllamaClient,
        episodic_store: EpisodicStore,
        semantic_store: SemanticStore,
        identity_store: IdentityStore,
        sentinel: Sentinel,
        tools: dict[str, Callable],
        soul_spec: str = "",
    ):
        self.llm = llm
        self.episodic = episodic_store
        self.semantic = semantic_store
        self.identity = identity_store
        self.sentinel = sentinel
        self.tools = tools
        self.soul_spec = soul_spec

    async def handle_task(self, task: str, context: dict = None) -> TaskResult:
        if context is None:
            context = {}
        start_time = time.monotonic()

        if not task.strip():
            return TaskResult(
                task=task, success=False, confidence=0.0,
                response="Empty task received.", tokens_used=0, latency_ms=0,
            )

        # Check if the task itself contains destructive content
        vigil_action = AgentAction(action_type="user_request", target=task)
        vigil_check = await self.sentinel.evaluate(vigil_action)
        if not vigil_check.approved:
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            trace = EpisodicTrace(
                task=task, context=context, decision="blocked_by_vigil",
                outcome=f"Blocked: {vigil_check.reason}", success=False,
                confidence=1.0, latency_ms=elapsed_ms, tokens_used=0,
            )
            await self.episodic.log_trace(trace)
            await self.identity.update_stats(task_success=False)
            return TaskResult(
                task=task, success=False, confidence=1.0,
                response=f"I cannot do that. {vigil_check.reason}",
                vigil_flags=[vigil_check.reason],
                tokens_used=0, latency_ms=elapsed_ms,
            )

        rules = await self.semantic.get_all_rules()
        rules_text = "\n".join(
            [f"- {r.rule} (confidence: {r.confidence:.0%})" for r in rules]
        ) if rules else "None yet — still learning from experience."

        identity = await self.identity.get_identity()
        tool_descriptions = ", ".join(self.tools.keys()) if self.tools else "none"

        system_prompt = AGENT_SYSTEM_PROMPT.format(
            agent_name=identity.name if identity else "Romulus",
            soul_spec=self.soul_spec,
            rules=rules_text,
            datetime=datetime.utcnow().isoformat(),
            total_tasks=identity.total_tasks if identity else 0,
            trust_score=f"{identity.trust_score:.0%}" if identity else "50%",
            tools=tool_descriptions,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task},
        ]

        try:
            llm_response = await self.llm.chat(messages, max_tokens=512)
        except Exception as e:
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            return TaskResult(
                task=task, success=False, confidence=0.0,
                response=f"LLM error: {e}", tokens_used=0, latency_ms=elapsed_ms,
            )

        parsed = self._parse_response(llm_response.text)

        action_outcome = None
        if parsed.action and parsed.action != "respond" and parsed.action in self.tools:
            action = AgentAction(
                action_type="tool_call", target=parsed.action, parameters=parsed.params,
            )
            verdict = await self.sentinel.evaluate(action)
            if verdict.approved:
                try:
                    tool_fn = self.tools[parsed.action]
                    if parsed.params:
                        tool_result = await tool_fn(**parsed.params)
                    else:
                        tool_result = await tool_fn()
                    action_outcome = ActionOutcome(
                        action=action, verdict=verdict, executed=True, result=str(tool_result),
                    )
                except Exception as e:
                    action_outcome = ActionOutcome(
                        action=action, verdict=verdict, executed=False, error=str(e),
                    )
            else:
                action_outcome = ActionOutcome(
                    action=action, verdict=verdict, executed=False, error=verdict.reason,
                )

        response_text = parsed.response or parsed.thought
        if action_outcome and action_outcome.executed:
            response_text += f"\n\n[Tool: {parsed.action}] {action_outcome.result}"
        elif action_outcome and not action_outcome.executed and action_outcome.error:
            response_text += f"\n\n[Tool blocked: {action_outcome.error}]"

        success = bool(parsed.response or (action_outcome and action_outcome.executed))
        elapsed_ms = int((time.monotonic() - start_time) * 1000)

        vigil_flags = []
        if action_outcome and not action_outcome.verdict.approved:
            vigil_flags.append(action_outcome.verdict.reason)

        result = TaskResult(
            task=task, success=success, confidence=parsed.confidence,
            response=response_text, vigil_flags=vigil_flags,
            tokens_used=llm_response.tokens_used, latency_ms=elapsed_ms,
        )

        trace = EpisodicTrace(
            task=task, context=context, decision=parsed.action or "respond",
            outcome=response_text[:500], success=success,
            confidence=parsed.confidence, latency_ms=elapsed_ms,
            tokens_used=llm_response.tokens_used,
            tools_used=[parsed.action] if parsed.action and parsed.action != "respond" else [],
            alternatives_considered=parsed.alternatives,
        )
        await self.episodic.log_trace(trace)
        await self.identity.update_stats(task_success=success)

        return result

    def _parse_response(self, text: str) -> ParsedResponse:
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        json_text = json_match.group(1).strip() if json_match else text.strip()

        if not json_text.startswith("{"):
            brace_start = json_text.find("{")
            if brace_start >= 0:
                brace_end = json_text.rfind("}") + 1
                if brace_end > brace_start:
                    json_text = json_text[brace_start:brace_end]

        try:
            data = json.loads(json_text)
            return ParsedResponse(
                thought=data.get("thought", ""),
                action=data.get("action", "respond"),
                params=data.get("params", {}),
                response=data.get("response", ""),
                confidence=min(1.0, max(0.0, float(data.get("confidence", 0.5)))),
            )
        except (json.JSONDecodeError, ValueError, TypeError):
            return ParsedResponse(
                thought="",
                action="respond",
                response=text.strip(),
                confidence=0.5,
            )
