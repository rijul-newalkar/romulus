from romulus.models.actions import AgentAction
from romulus.models.vigil import VigilVerdict
from romulus.vigil.adaptive import AdaptiveLayer
from romulus.vigil.incidents import IncidentLogger
from romulus.vigil.innate import InnateLayer


class Sentinel:
    def __init__(self, innate: InnateLayer, adaptive: AdaptiveLayer, incident_logger: IncidentLogger):
        self.innate = innate
        self.adaptive = adaptive
        self.incident_logger = incident_logger

    async def evaluate(self, action: AgentAction) -> VigilVerdict:
        verdict = self.innate.check(action)
        if not verdict.approved:
            await self.incident_logger.log(action, verdict)
            return verdict

        verdict = await self.adaptive.check(action)
        if not verdict.approved:
            await self.incident_logger.log(action, verdict)
            return verdict

        return VigilVerdict(approved=True, layer="all_clear")
