from romulus.chronicle.database import ChronicleDB
from romulus.models.actions import AgentAction
from romulus.models.vigil import ThreatCategory, VigilVerdict


class MemoryCell:
    def __init__(self, pattern: str, category: str, reason: str):
        self.pattern = pattern.lower()
        self.category = category
        self.reason = reason


class AdaptiveLayer:
    def __init__(self, db: ChronicleDB):
        self.db = db
        self._memory_cells: list[MemoryCell] = []

    async def load_memory_cells(self):
        rows = await self.db.execute(
            "SELECT DISTINCT target, category, reason FROM vigil_incidents WHERE blocked = 1"
        )
        self._memory_cells = [
            MemoryCell(
                pattern=row["target"],
                category=row["category"],
                reason=f"Previously blocked: {row['reason']}",
            )
            for row in rows
        ]

    async def check(self, action: AgentAction) -> VigilVerdict:
        target_lower = action.target.lower()
        params_lower = str(action.parameters).lower()
        full_text = f"{target_lower} {params_lower}"

        for cell in self._memory_cells:
            if cell.pattern in full_text:
                return VigilVerdict(
                    approved=False,
                    category=ThreatCategory(cell.category),
                    layer="adaptive",
                    reason=cell.reason,
                )

        return VigilVerdict(approved=True, layer="adaptive")

    async def add_memory_cell(self, pattern: str, category: str, reason: str):
        self._memory_cells.append(MemoryCell(pattern, category, reason))
