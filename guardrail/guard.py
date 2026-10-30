from . import policy, context, nemotron, tools
from .behavior import BehaviorTracker
from .fusion import fuse
from .audit import AuditLog
from .models import Action


class GuardedExecutor:
    """Intercepts every action BEFORE it runs. allow -> execute, review -> hold, block -> refuse."""

    def __init__(self, client=None, audit_path="audit_log.jsonl"):
        self.client = client
        self.behavior = BehaviorTracker()
        self.audit = AuditLog(audit_path)

    def evaluate(self, a: Action):
        signals, reasons = {}, []
        for name, (s, why) in (("policy", policy.score(a)), ("context", context.score(a)),
                               ("behavior", self.behavior.score(a))):
            signals[name] = s; reasons += why
        rationale = ""
        j = nemotron.judge(self.client, a)
        if j:
            signals["nemotron"], rationale = j
        return fuse(signals, reasons, rationale)

    def run(self, a: Action):
        v = self.evaluate(a)
        result = tools.execute(a) if v.decision == "allow" else None
        if v.decision == "allow":
            self.behavior.observe(a)
        h = self.audit.append({"agent": a.agent_id, "tool": a.tool, "args": a.args,
                               "task": a.user_task, "decision": v.decision, "risk": v.risk,
                               "signals": v.signals, "reasons": v.reasons})
        return v, result, h
