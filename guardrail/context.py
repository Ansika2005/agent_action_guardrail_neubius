"""Signal 2: contextual sensitivity (what data, going where)."""
import re
from urllib.parse import urlparse
from .models import Action

INTERNAL_DOMAINS = {"acme-retail.com"}
PII = {
    "email": r"[\w.+-]+@[\w-]+\.[\w.]+",
    "phone": r"\b(?:\+91[- ]?)?[6-9]\d{9}\b",
    "aadhaar": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
    "card": r"\b(?:\d[ -]?){13,16}\b",
    "pan": r"\b[A-Z]{5}\d{4}[A-Z]\b",
}
SECRETS = [r"\bsk-[A-Za-z0-9_-]{16,}", r"AKIA[0-9A-Z]{16}",
           r"-----BEGIN [A-Z ]*PRIVATE KEY-----", r"(?i)password\s*[:=]\s*\S+"]
EXTERNAL_TOOLS = {"send_email", "http_post"}


def _destination(a: Action):
    dest = a.args.get("to") or a.args.get("url") or ""
    if "@" in dest:
        return dest.split("@")[-1].lower()
    return (urlparse(dest).hostname or "").lower()


def score(a: Action):
    text = a.flat(skip=("to", "url"))
    kinds = [k for k, p in PII.items() if re.search(p, text)]
    secret = any(re.search(p, text) for p in SECRETS)
    s = min(1.0, 0.35 * len(kinds) + (0.6 if secret else 0))
    why = []
    if kinds: why.append("context: PII detected (" + ", ".join(kinds) + ")")
    if secret: why.append("context: secret/credential material in payload")
    if a.tool in EXTERNAL_TOOLS:
        d = _destination(a)
        if d and d not in INTERNAL_DOMAINS:
            why.append(f"context: external destination {d}")
            s = min(1.0, s + 0.3) if s > 0 else 0.15
    return s, why
