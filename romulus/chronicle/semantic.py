import json
from datetime import datetime

from romulus.chronicle.database import ChronicleDB
from romulus.models.semantic import SemanticRule


class SemanticStore:
    def __init__(self, db: ChronicleDB):
        self.db = db

    async def add_rule(self, rule: SemanticRule) -> str:
        await self.db.execute_insert(
            """INSERT INTO semantic_rules
               (id, rule, confidence, evidence_count, last_validated,
                contradictions, domain, source_episode_ids)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                rule.id,
                rule.rule,
                rule.confidence,
                rule.evidence_count,
                rule.last_validated.isoformat(),
                rule.contradictions,
                rule.domain,
                json.dumps(rule.source_episode_ids),
            ),
        )
        return rule.id

    async def get_all_rules(self, domain: str | None = None) -> list[SemanticRule]:
        if domain:
            rows = await self.db.execute(
                "SELECT * FROM semantic_rules WHERE domain = ? ORDER BY confidence DESC",
                (domain,),
            )
        else:
            rows = await self.db.execute(
                "SELECT * FROM semantic_rules ORDER BY confidence DESC"
            )
        return [self._row_to_rule(row) for row in rows]

    async def get_rule(self, rule_id: str) -> SemanticRule | None:
        rows = await self.db.execute(
            "SELECT * FROM semantic_rules WHERE id = ?", (rule_id,)
        )
        if not rows:
            return None
        return self._row_to_rule(rows[0])

    async def validate_rule(self, rule_id: str):
        await self.db.execute(
            """UPDATE semantic_rules
               SET evidence_count = evidence_count + 1, last_validated = ?
               WHERE id = ?""",
            (datetime.utcnow().isoformat(), rule_id),
        )

    async def invalidate_rule(self, rule_id: str):
        await self.db.execute(
            "UPDATE semantic_rules SET contradictions = contradictions + 1 WHERE id = ?",
            (rule_id,),
        )
        rows = await self.db.execute(
            "SELECT evidence_count, contradictions FROM semantic_rules WHERE id = ?",
            (rule_id,),
        )
        if rows and rows[0]["contradictions"] > rows[0]["evidence_count"]:
            await self.db.execute(
                "DELETE FROM semantic_rules WHERE id = ?", (rule_id,)
            )

    async def count_rules(self) -> int:
        rows = await self.db.execute("SELECT COUNT(*) as cnt FROM semantic_rules")
        return rows[0]["cnt"] if rows else 0

    def _row_to_rule(self, row: dict) -> SemanticRule:
        return SemanticRule(
            id=row["id"],
            rule=row["rule"],
            confidence=row["confidence"],
            evidence_count=row["evidence_count"],
            last_validated=datetime.fromisoformat(row["last_validated"]),
            contradictions=row["contradictions"],
            domain=row["domain"],
            source_episode_ids=json.loads(row["source_episode_ids"]),
        )
