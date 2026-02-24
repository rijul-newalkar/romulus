import json
from datetime import datetime
from uuid import uuid4

from romulus.chronicle.database import ChronicleDB
from romulus.chronicle.episodic import EpisodicStore
from romulus.chronicle.semantic import SemanticStore
from romulus.dream.extractor import RuleExtractor
from romulus.dream.pruner import MemoryPruner
from romulus.dream.replay import ReplayStage
from romulus.llm.client import OllamaClient
from romulus.llm.prompts import DREAM_SUMMARY_PROMPT
from romulus.models.dream import DreamReport


class DreamEngine:
    def __init__(
        self,
        llm: OllamaClient,
        episodic_store: EpisodicStore,
        semantic_store: SemanticStore,
        chronicle_db: ChronicleDB,
    ):
        self.llm = llm
        self.episodic = episodic_store
        self.semantic = semantic_store
        self.db = chronicle_db
        self.replay = ReplayStage(llm)
        self.extractor = RuleExtractor(llm)
        self.pruner = MemoryPruner(episodic_store)

    async def run_dream_cycle(self, hours_to_review: int = 24) -> DreamReport:
        report = DreamReport()

        episodes = await self.episodic.get_traces_for_dream(hours=hours_to_review)
        report.episodes_processed = len(episodes)

        if not episodes:
            report.summary = "No episodes to process. The agent had no experiences to dream about."
            await self._save_report(report)
            return report

        replay_summary = await self.replay.analyze(episodes)

        new_rules = await self.extractor.extract_rules(episodes, replay_summary)
        for rule in new_rules:
            await self.semantic.add_rule(rule)
        report.new_rules_extracted = new_rules

        existing_rules = await self.semantic.get_all_rules()
        invalidated = await self.extractor.validate_existing_rules(existing_rules, episodes)
        for rule_id in invalidated:
            await self.semantic.invalidate_rule(rule_id)
        report.rules_invalidated = invalidated

        pruned = await self.pruner.prune(older_than_days=14)
        report.memories_pruned = pruned

        report.summary = await self._generate_summary(report)
        await self._save_report(report)

        return report

    async def _generate_summary(self, report: DreamReport) -> str:
        rules_text = "\n".join(
            [f"- {r.rule} (confidence: {r.confidence:.0%})" for r in report.new_rules_extracted]
        ) if report.new_rules_extracted else "None"

        prompt = DREAM_SUMMARY_PROMPT.format(
            episodes_processed=report.episodes_processed,
            new_rules_count=len(report.new_rules_extracted),
            rules_invalidated_count=len(report.rules_invalidated),
            memories_pruned=report.memories_pruned,
            confidence_adjustment=report.confidence_adjustment,
            new_rules=rules_text,
        )

        try:
            response = await self.llm.generate(
                prompt,
                system="You are writing a concise dream cycle summary. Be brief and informative.",
                temperature=0.5,
                max_tokens=256,
            )
            return response.text.strip()
        except Exception:
            return (
                f"Processed {report.episodes_processed} episodes. "
                f"Extracted {len(report.new_rules_extracted)} new rules. "
                f"Pruned {report.memories_pruned} old memories."
            )

    async def _save_report(self, report: DreamReport):
        rules_json = json.dumps([r.model_dump() for r in report.new_rules_extracted], default=str)
        await self.db.execute_insert(
            """INSERT INTO dream_reports
               (id, date, episodes_processed, counterfactuals_run, new_rules,
                rules_invalidated, memories_pruned, weak_spots,
                confidence_adjustment, summary)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                report.id,
                report.date.isoformat(),
                report.episodes_processed,
                report.counterfactuals_run,
                rules_json,
                json.dumps(report.rules_invalidated),
                report.memories_pruned,
                json.dumps(report.weak_spots_found),
                report.confidence_adjustment,
                report.summary,
            ),
        )
