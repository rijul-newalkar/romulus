import json
from pathlib import Path

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS episodic_traces (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    task TEXT NOT NULL,
    context TEXT DEFAULT '{}',
    decision TEXT NOT NULL,
    tools_used TEXT DEFAULT '[]',
    outcome TEXT NOT NULL,
    success INTEGER NOT NULL,
    confidence REAL NOT NULL,
    latency_ms INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    alternatives_considered TEXT DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS semantic_rules (
    id TEXT PRIMARY KEY,
    rule TEXT NOT NULL,
    confidence REAL NOT NULL,
    evidence_count INTEGER DEFAULT 1,
    last_validated TEXT NOT NULL,
    contradictions INTEGER DEFAULT 0,
    domain TEXT DEFAULT 'general',
    source_episode_ids TEXT DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS agent_identity (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT DEFAULT '0.1.0',
    created_at TEXT NOT NULL,
    soul_spec TEXT DEFAULT '',
    total_tasks INTEGER DEFAULT 0,
    successful_tasks INTEGER DEFAULT 0,
    trust_score REAL DEFAULT 0.5,
    total_uptime_seconds INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS dream_reports (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    episodes_processed INTEGER DEFAULT 0,
    counterfactuals_run INTEGER DEFAULT 0,
    new_rules TEXT DEFAULT '[]',
    rules_invalidated TEXT DEFAULT '[]',
    memories_pruned INTEGER DEFAULT 0,
    weak_spots TEXT DEFAULT '[]',
    confidence_adjustment REAL DEFAULT 0.0,
    summary TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS vigil_incidents (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    action_type TEXT NOT NULL,
    target TEXT NOT NULL,
    category TEXT NOT NULL,
    layer TEXT NOT NULL,
    reason TEXT NOT NULL,
    blocked INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_traces_timestamp ON episodic_traces(timestamp);
CREATE INDEX IF NOT EXISTS idx_traces_success ON episodic_traces(success);
CREATE INDEX IF NOT EXISTS idx_rules_domain ON semantic_rules(domain);
CREATE INDEX IF NOT EXISTS idx_vigil_timestamp ON vigil_incidents(timestamp);
"""


class ChronicleDB:
    def __init__(self, db_path: str = "data/chronicle.db"):
        self.db_path = db_path

    async def initialize(self):
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(SCHEMA)
            await db.commit()

    async def connect(self) -> aiosqlite.Connection:
        db = await aiosqlite.connect(self.db_path)
        db.row_factory = aiosqlite.Row
        return db

    async def execute(self, query: str, params: tuple = ()) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            await db.commit()
            return [dict(row) for row in rows]

    async def execute_insert(self, query: str, params: tuple = ()) -> str:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, params)
            await db.commit()
            return params[0] if params else ""

    async def execute_many(self, query: str, params_list: list[tuple]):
        async with aiosqlite.connect(self.db_path) as db:
            await db.executemany(query, params_list)
            await db.commit()
