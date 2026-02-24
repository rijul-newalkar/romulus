from datetime import datetime
from uuid import uuid4

from romulus.chronicle.database import ChronicleDB
from romulus.models.identity import AgentIdentity


class IdentityStore:
    def __init__(self, db: ChronicleDB):
        self.db = db

    async def get_or_create_identity(self, name: str, soul_spec: str = "") -> AgentIdentity:
        rows = await self.db.execute("SELECT * FROM agent_identity LIMIT 1")
        if rows:
            return self._row_to_identity(rows[0])

        identity = AgentIdentity(
            id=str(uuid4()),
            name=name,
            soul_spec=soul_spec,
            created_at=datetime.utcnow(),
        )
        await self.db.execute_insert(
            """INSERT INTO agent_identity
               (id, name, version, created_at, soul_spec, total_tasks,
                successful_tasks, trust_score, total_uptime_seconds)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                identity.id,
                identity.name,
                identity.version,
                identity.created_at.isoformat(),
                identity.soul_spec,
                identity.total_tasks,
                identity.successful_tasks,
                identity.trust_score,
                identity.total_uptime_seconds,
            ),
        )
        return identity

    async def get_identity(self) -> AgentIdentity | None:
        rows = await self.db.execute("SELECT * FROM agent_identity LIMIT 1")
        if not rows:
            return None
        return self._row_to_identity(rows[0])

    async def update_stats(self, task_success: bool):
        if task_success:
            await self.db.execute(
                "UPDATE agent_identity SET total_tasks = total_tasks + 1, successful_tasks = successful_tasks + 1"
            )
        else:
            await self.db.execute(
                "UPDATE agent_identity SET total_tasks = total_tasks + 1"
            )
        await self._recalculate_trust()

    async def _recalculate_trust(self):
        rows = await self.db.execute(
            "SELECT total_tasks, successful_tasks FROM agent_identity LIMIT 1"
        )
        if rows and rows[0]["total_tasks"] > 0:
            trust = rows[0]["successful_tasks"] / rows[0]["total_tasks"]
            trust = 0.5 + (trust - 0.5) * min(rows[0]["total_tasks"] / 50, 1.0)
            await self.db.execute(
                "UPDATE agent_identity SET trust_score = ?", (round(trust, 4),)
            )

    def _row_to_identity(self, row: dict) -> AgentIdentity:
        return AgentIdentity(
            id=row["id"],
            name=row["name"],
            version=row["version"],
            created_at=datetime.fromisoformat(row["created_at"]),
            soul_spec=row["soul_spec"],
            total_tasks=row["total_tasks"],
            successful_tasks=row["successful_tasks"],
            trust_score=row["trust_score"],
            total_uptime_seconds=row["total_uptime_seconds"],
        )
