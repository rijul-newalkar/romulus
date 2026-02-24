from datetime import datetime, timedelta
from uuid import uuid4

from romulus.chronicle.database import ChronicleDB
from romulus.models.actions import AgentAction
from romulus.models.vigil import VigilVerdict


class IncidentLogger:
    def __init__(self, db: ChronicleDB):
        self.db = db

    async def log(self, action: AgentAction, verdict: VigilVerdict):
        await self.db.execute_insert(
            """INSERT INTO vigil_incidents
               (id, timestamp, action_type, target, category, layer, reason, blocked)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(uuid4()),
                datetime.utcnow().isoformat(),
                action.action_type,
                action.target,
                verdict.category.value if verdict.category else "unknown",
                verdict.layer,
                verdict.reason,
                int(not verdict.approved),
            ),
        )

    async def get_recent_incidents(self, hours: int = 24) -> list[dict]:
        since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        return await self.db.execute(
            "SELECT * FROM vigil_incidents WHERE timestamp >= ? ORDER BY timestamp DESC",
            (since,),
        )

    async def get_incident_count(self, hours: int = 24) -> int:
        since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        rows = await self.db.execute(
            "SELECT COUNT(*) as cnt FROM vigil_incidents WHERE timestamp >= ?",
            (since,),
        )
        return rows[0]["cnt"] if rows else 0
