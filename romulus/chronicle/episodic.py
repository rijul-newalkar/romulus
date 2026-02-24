import json
from datetime import datetime, timedelta

from romulus.chronicle.database import ChronicleDB
from romulus.models.episodic import EpisodicTrace


class EpisodicStore:
    def __init__(self, db: ChronicleDB):
        self.db = db

    async def log_trace(self, trace: EpisodicTrace) -> str:
        await self.db.execute_insert(
            """INSERT INTO episodic_traces
               (id, timestamp, task, context, decision, tools_used, outcome,
                success, confidence, latency_ms, tokens_used, alternatives_considered)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                trace.id,
                trace.timestamp.isoformat(),
                trace.task,
                json.dumps(trace.context),
                trace.decision,
                json.dumps(trace.tools_used),
                trace.outcome,
                int(trace.success),
                trace.confidence,
                trace.latency_ms,
                trace.tokens_used,
                json.dumps(trace.alternatives_considered),
            ),
        )
        return trace.id

    async def get_traces(
        self,
        since: datetime | None = None,
        limit: int = 100,
        success: bool | None = None,
    ) -> list[EpisodicTrace]:
        query = "SELECT * FROM episodic_traces WHERE 1=1"
        params: list = []

        if since is not None:
            query += " AND timestamp >= ?"
            params.append(since.isoformat())
        if success is not None:
            query += " AND success = ?"
            params.append(int(success))

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        rows = await self.db.execute(query, tuple(params))
        return [self._row_to_trace(row) for row in rows]

    async def get_traces_for_dream(self, hours: int = 24) -> list[EpisodicTrace]:
        since = datetime.utcnow() - timedelta(hours=hours)
        return await self.get_traces(since=since, limit=500)

    async def count_traces(self, since: datetime | None = None) -> int:
        if since:
            rows = await self.db.execute(
                "SELECT COUNT(*) as cnt FROM episodic_traces WHERE timestamp >= ?",
                (since.isoformat(),),
            )
        else:
            rows = await self.db.execute("SELECT COUNT(*) as cnt FROM episodic_traces")
        return rows[0]["cnt"] if rows else 0

    async def delete_old_traces(self, older_than_days: int = 14, keep_failures: bool = True) -> int:
        cutoff = (datetime.utcnow() - timedelta(days=older_than_days)).isoformat()
        if keep_failures:
            rows = await self.db.execute(
                "SELECT COUNT(*) as cnt FROM episodic_traces WHERE timestamp < ? AND success = 1",
                (cutoff,),
            )
            count = rows[0]["cnt"] if rows else 0
            await self.db.execute(
                "DELETE FROM episodic_traces WHERE timestamp < ? AND success = 1",
                (cutoff,),
            )
        else:
            rows = await self.db.execute(
                "SELECT COUNT(*) as cnt FROM episodic_traces WHERE timestamp < ?",
                (cutoff,),
            )
            count = rows[0]["cnt"] if rows else 0
            await self.db.execute(
                "DELETE FROM episodic_traces WHERE timestamp < ?",
                (cutoff,),
            )
        return count

    def _row_to_trace(self, row: dict) -> EpisodicTrace:
        return EpisodicTrace(
            id=row["id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            task=row["task"],
            context=json.loads(row["context"]),
            decision=row["decision"],
            tools_used=json.loads(row["tools_used"]),
            outcome=row["outcome"],
            success=bool(row["success"]),
            confidence=row["confidence"],
            latency_ms=row["latency_ms"],
            tokens_used=row["tokens_used"],
            alternatives_considered=json.loads(row["alternatives_considered"]),
        )
