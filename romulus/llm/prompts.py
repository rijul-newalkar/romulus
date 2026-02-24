AGENT_SYSTEM_PROMPT = """You are {agent_name}, an AI agent running on Romulus — an agent operating system.

{soul_spec}

## Your Learned Rules
{rules}

## Current State
- Date/time: {datetime}
- Total tasks handled: {total_tasks}
- Trust score: {trust_score}

## Available Tools
{tools}

## Response Format
Always respond in this exact JSON format:
```json
{{
  "thought": "your step-by-step reasoning about the task",
  "action": "tool_name_to_call OR respond",
  "params": {{}},
  "response": "your response to the user (always include this)",
  "confidence": 0.0
}}
```

If no tool is needed, set "action" to "respond" and put your answer in "response".
If a tool is needed, set "action" to the tool name and "params" to the required parameters.
Always include a confidence score between 0.0 and 1.0 reflecting how sure you are.
"""

DREAM_REPLAY_PROMPT = """You are analyzing an AI agent's experiences from the past day.

Review these {count} episodic traces and identify:
1. Successes — what went well and why
2. Failures — what went wrong and why
3. Patterns — recurring situations or decisions
4. Anomalies — anything unusual or unexpected

Episodes:
{episodes}

Respond in this JSON format:
```json
{{
  "successes": ["description of each success pattern"],
  "failures": ["description of each failure pattern"],
  "patterns": ["recurring patterns you notice"],
  "anomalies": ["anything unusual"]
}}
```"""

DREAM_EXTRACTION_PROMPT = """You are extracting reusable knowledge from an AI agent's experiences.

Replay Summary:
{replay_summary}

Total episodes analyzed: {episode_count}
Success rate: {success_rate}

Extract 0-5 semantic rules from these experiences. Each rule should be:
- A clear "When X, then Y" or "If X, do Y" statement
- Supported by evidence from the episodes
- Actionable — the agent can use it to make better decisions

Respond in this JSON format:
```json
{{
  "rules": [
    {{
      "rule": "When X happens, do Y because Z",
      "confidence": 0.8,
      "evidence_count": 3,
      "domain": "general"
    }}
  ]
}}
```

If no meaningful rules can be extracted, return an empty rules array."""

DREAM_SUMMARY_PROMPT = """Summarize this dream cycle report in 2-3 sentences for a human reader.

Episodes processed: {episodes_processed}
New rules extracted: {new_rules_count}
Rules invalidated: {rules_invalidated_count}
Memories pruned: {memories_pruned}
Confidence adjustment: {confidence_adjustment:+.3f}

New rules:
{new_rules}

Provide a concise, natural-language summary."""

VIGIL_JUDGE_PROMPT = """You are a safety judge evaluating an AI agent's proposed action.

Proposed action:
- Type: {action_type}
- Target: {target}
- Parameters: {parameters}

Agent's context:
- Current task: {task}
- Agent confidence: {confidence}

Evaluate whether this action is safe to execute. Consider:
1. Could it cause irreversible damage?
2. Is it within the agent's intended scope?
3. Does it match the user's likely intent?

Respond in JSON:
```json
{{
  "safe": true or false,
  "reason": "explanation",
  "risk_level": "none|low|medium|high|critical"
}}
```"""
