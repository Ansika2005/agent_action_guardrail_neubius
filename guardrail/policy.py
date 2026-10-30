"""Signal 1: hard policy compliance (deterministic rules)."""
import re
from .models import Action

DESTRUCTIVE = [
    (r"\brm\s+-[a-z]*r[a-z]*f", "recursive force delete"),
    (r"\bdrop\s+(table|database)\b", "destructive SQL (DROP)"),
    (r"\bdelete\s+from\b(?!.*\bwhere\b)", "DELETE without WHERE"),
    (r"curl[^|]*\|\s*(ba)?sh", "pipe remote script to shell"),
    (r"\bmkfs\b|chmod\s+-R\s+777", "dangerous system command"),
]
SENSITIVE_PATHS = [r"\.env\b", r"id_rsa", r"/etc/(passwd|shadow)", r"credentials", r"\.aws/"]
PAYMENT_LIMIT_REVIEW = 1_000
PAYMENT_LIMIT_BLOCK = 10_000


def score(a: Action):
    s, why = 0.0, []
    text = a.flat().lower()
    if a.tool in ("run_shell", "query_db"):
        for pat, label in DESTRUCTIVE:
            if re.search(pat, text):
                s = max(s, 1.0); why.append(f"policy: {label}")
    if a.tool in ("read_file", "run_shell"):
        for pat in SENSITIVE_PATHS:
            if re.search(pat, text):
                s = max(s, 0.8); why.append("policy: access to credential/secret path")
                break
    if a.tool == "transfer_funds":
        amt = float(a.args.get("amount", 0) or 0)
        if amt >= PAYMENT_LIMIT_BLOCK:
            s = max(s, 0.9); why.append(f"policy: payment {amt:,.0f} exceeds hard limit")
        elif amt >= PAYMENT_LIMIT_REVIEW:
            s = max(s, 0.5); why.append(f"policy: payment {amt:,.0f} needs approval")
    return s, why
