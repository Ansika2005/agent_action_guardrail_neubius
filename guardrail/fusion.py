"""Risk Fusion: combine signals, escalate on strong single signals, explain contributions."""
from .models import Verdict

WEIGHTS = {"policy": 0.35, "context": 0.20, "behavior": 0.15, "nemotron": 0.30}
REVIEW_AT, BLOCK_AT, ESCALATE_AT = 0.35, 0.70, 0.70


def fuse(signals: dict, reasons: list, rationale: str = "") -> Verdict:
    w = {k: v for k, v in WEIGHTS.items() if k in signals}
    norm = sum(w.values())
    contrib = {k: round(w[k] / norm * signals[k], 3) for k in w}   # additive attribution
    risk = sum(contrib.values())
    top = max(signals.values())
    if top >= ESCALATE_AT:                      # one strong signal must not be averaged away
        esc = 0.85 * top
        if esc > risk:
            contrib["escalation"] = round(esc - risk, 3)
            risk = esc
    decision = "block" if risk >= BLOCK_AT else "review" if risk >= REVIEW_AT else "allow"
    return Verdict(decision, round(risk, 3), signals, contrib, reasons, rationale)
