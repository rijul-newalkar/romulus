import json
import re

from romulus.dream.replay import ReplaySummary
from romulus.llm.client import OllamaClient
from romulus.llm.prompts import DREAM_EXTRACTION_PROMPT
from romulus.models.episodic import EpisodicTrace
from romulus.models.semantic import SemanticRule


class RuleExtractor:
    def __init__(self, llm: OllamaClient):
        self.llm = llm

    async def extract_rules(
        self, episodes: list[EpisodicTrace], replay_summary: ReplaySummary
    ) -> list[SemanticRule]:
        if not episodes:
            return []

        success_count = sum(1 for e in episodes if e.success)
        success_rate = f"{success_count}/{len(episodes)} ({success_count / len(episodes):.0%})"

        summary_text = (
            f"Successes: {replay_summary.successes}\n"
            f"Failures: {replay_summary.failures}\n"
            f"Patterns: {replay_summary.patterns}\n"
            f"Anomalies: {replay_summary.anomalies}"
        )

        prompt = DREAM_EXTRACTION_PROMPT.format(
            replay_summary=summary_text,
            episode_count=len(episodes),
            success_rate=success_rate,
        )

        response = await self.llm.generate(
            prompt,
            system="You are extracting reusable knowledge from experience. Respond only with valid JSON.",
            temperature=0.3,
            max_tokens=1024,
        )

        return self._parse_rules(response.text, episodes)

    async def validate_existing_rules(
        self, rules: list[SemanticRule], episodes: list[EpisodicTrace]
    ) -> list[str]:
        if not rules or not episodes:
            return []

        invalidated = []
        for rule in rules:
            if rule.contradictions > rule.evidence_count:
                invalidated.append(rule.id)

        return invalidated

    def _parse_rules(self, text: str, episodes: list[EpisodicTrace]) -> list[SemanticRule]:
        try:
            json_text = text.strip()
            if "```" in json_text:
                match = re.search(r"```(?:json)?\s*([\s\S]*?)```", json_text)
                if match:
                    json_text = match.group(1).strip()

            start = json_text.find("{")
            end = json_text.rfind("}") + 1
            if start >= 0 and end > start:
                json_text = json_text[start:end]

            data = json.loads(json_text)
            raw_rules = data.get("rules", [])

            episode_ids = [e.id for e in episodes[:10]]
            result = []

            for r in raw_rules:
                rule_text = r.get("rule", "").strip()
                if len(rule_text) < 10:
                    continue
                confidence = min(1.0, max(0.0, float(r.get("confidence", 0.7))))
                if confidence < 0.5:
                    continue

                result.append(SemanticRule(
                    rule=rule_text,
                    confidence=confidence,
                    evidence_count=int(r.get("evidence_count", 1)),
                    domain=r.get("domain", "general"),
                    source_episode_ids=episode_ids,
                ))

            return result

        except (json.JSONDecodeError, ValueError, TypeError):
            return []
