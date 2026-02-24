from pydantic import BaseModel

from romulus.models.vigil import VigilVerdict


class AgentAction(BaseModel):
    action_type: str
    target: str
    parameters: dict = {}
    reversible: bool = True


class ActionOutcome(BaseModel):
    action: AgentAction
    verdict: VigilVerdict
    executed: bool
    result: str = ""
    error: str = ""
