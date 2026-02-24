from romulus.chronicle.episodic import EpisodicStore


class MemoryPruner:
    def __init__(self, episodic_store: EpisodicStore):
        self.episodic = episodic_store

    async def prune(self, older_than_days: int = 14) -> int:
        return await self.episodic.delete_old_traces(
            older_than_days=older_than_days,
            keep_failures=True,
        )
