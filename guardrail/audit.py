"""Tamper-evident audit trail: each record commits to the previous one (hash chain).
The head hash can be anchored on-chain (see README roadmap: Hardhat/Sepolia)."""
import hashlib, json, os, time


class AuditLog:
    def __init__(self, path="audit_log.jsonl"):
        self.path = path

    def entries(self):
        if not os.path.exists(self.path):
            return []
        with open(self.path) as f:
            return [json.loads(l) for l in f]

    def _last(self):
        e = self.entries()
        return e[-1]["hash"] if e else "0" * 64

    def append(self, record: dict) -> str:
        body = {"ts": time.time(), "prev": self._last(), **record}
        h = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        with open(self.path, "a") as f:
            f.write(json.dumps({**body, "hash": h}) + "\n")
        return h

    def verify(self) -> bool:
        prev = "0" * 64
        for e in self.entries():
            h = e.pop("hash")
            if e["prev"] != prev or hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest() != h:
                return False
            prev = h
        return True
