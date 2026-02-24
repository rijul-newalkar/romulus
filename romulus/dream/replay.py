import json

from pydantic import BaseModel

from romulus.llm.client import OllamaClient
from romulus.llm.prompts import DREAM_REPLAY_PROMPT
from romulus.models.episodic import EpisodicTrace


class ReplaySummary(BaseModel):
    successes: list[str] = []
    failures: list[str] = []
    patterns: list[str] = []
    anomalies: list[str] = []


class ReplayStage:
    def __init__(self, llm: OllamaClient):
        self.llm = llm

    async def analyze(self, episodes: list[EpisodicTrace]) -> ReplaySummary:
        episodes_text = self._format_episodes(episodes)
        prompt = DREAM_REPLAY_PROMPT.format(
            count=len(episodes),
            episodes=episodes_text,
        )

        response = await self.llm.generate(
            prompt,
            system="You are an analytical AI reviewing agent performance logs. Respond only with valid JSON.",
            temperature=0.3,
            max_tokens=1024,
        )

        return self._parse_summary(response.text)

    def _format_episodes(self, episodes: list[EpisodicTrace]) -> str:
        lines = []
        for i, ep in enumerate(episodes[:50], 1):
            status = "SUCCESS" if ep.success else "FAILURE"
            lines.append(
                f"{i}. [{status}] Task: {ep.task} | Decision: {ep.decision} | "
                f"Outcome: {ep.outcome[:100]} | Confidence: {ep.confidence:.0%}"
            )
        return "\n".join(lines)

    def _parse_summary(self, text: str) -> ReplaySummary:
        try:
            json_text = text.strip()
            if "```" in json_text:
                import re
                match = re.search(r"```(?:json)?\s*([\s\S]*?)```", json_text)
                if match:
                    json_text = match.group(1).strip()

            start = json_text.find("{")
            end = json_text.rfind("}") + 1
            if start >= 0 and end > start:
                json_text = json_text[start:end]

            data = json.loads(json_text)
            return ReplaySummary(
                successes=data.get("successes", []),
                failures=data.get("failures", []),
                patterns=data.get("patterns", []),
                anomalies=data.get("anomalies", []),
            )
        except (json.JSONDecodeError, ValueError):
            return ReplaySummary(
                patterns=[f"Raw analysis: {text[:500]}"],
            )
