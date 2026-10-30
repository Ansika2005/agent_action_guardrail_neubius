"""Signal 3: behavioral deviation from the agent's own baseline."""
import time
from collections import Counter, defaultdict, deque
from .models import Action


class BehaviorTracker:
    def __init__(self):
        self.counts = defaultdict(Counter)
        self.recent = defaultdict(lambda: deque(maxlen=50))

    def seed(self, agent_id, tool, n=10):
        self.counts[agent_id][tool] += n

    def score(self, a: Action):
        c, total = self.counts[a.agent_id], sum(self.counts[a.agent_id].values())
        s, why = 0.1, []
        if total >= 5:
            freq = c[a.tool] / total
            if c[a.tool] == 0:
                s = 0.8; why.append(f"behavior: first use of '{a.tool}' by {a.agent_id}")
            elif freq < 0.1:
                s = 0.5; why.append(f"behavior: '{a.tool}' is rare for {a.agent_id}")
        now = time.time()
        burst = sum(1 for t in self.recent[a.agent_id] if now - t < 60)
        if burst >= 8:
            s = min(1.0, s + 0.3); why.append("behavior: burst of calls in 60s")
        return s, why

    def observe(self, a: Action):
        self.counts[a.agent_id][a.tool] += 1
        self.recent[a.agent_id].append(time.time())
