import json
from dataclasses import dataclass, field


@dataclass
class Action:
    """A tool call an AI agent wants to perform."""
    tool: str
    args: dict
    agent_id: str = "agent-1"
    user_task: str = ""

    def flat(self, skip=()) -> str:
        return json.dumps({k: v for k, v in self.args.items() if k not in skip},
                          ensure_ascii=False)


@dataclass
class Verdict:
    decision: str                 # allow | review | block
    risk: float
    signals: dict = field(default_factory=dict)         # name -> 0..1
    contributions: dict = field(default_factory=dict)   # name -> additive share of risk
    reasons: list = field(default_factory=list)
    rationale: str = ""           # Nemotron's natural-language explanation
