# 🛡️ AI Agent Action Guardrail

Action-level guardrails for AI agents: every tool call is intercepted **before execution**, scored by
four independent signals, fused into **allow / review / block**, explained, and written to a
tamper-evident audit log. Built on **NVIDIA Nemotron served by Nebius Token Factory**.

## How it works
| Signal | What it checks |
|---|---|
| Policy | Deterministic rules: destructive commands, secret paths, payment limits |
| Context | PII / secrets in the payload, internal vs external destination |
| Behavior | Deviation from the agent's own tool-usage baseline |
| **Nemotron judge** | Intent alignment with the user task, prompt injection, exfiltration; returns a rationale |

Risk Fusion = weighted sum + escalation (one very strong signal can't be averaged away). Each signal's
additive contribution is shown, so every decision is explainable. Decisions are appended to a
SHA-256 hash-chained audit log (`guardrail/audit.py`).

The demo also includes a **Nemotron-powered agent** that plans tool calls from a task plus an untrusted
document, so you can watch a prompt injection get planned by the agent and stopped by the guardrail.
All tools are sandboxed mocks.

## NVIDIA / Nebius usage
- **Nemotron** (`nvidia/nemotron-3-super-120b-a12b` by default, override with `NEBIUS_MODEL`) plays two roles: the
  agent planner and the security judge (`guardrail/nemotron.py`).
- **Nebius Token Factory** OpenAI-compatible endpoint (`https://api.tokenfactory.nebius.com/v1/`): low-latency
  inference matters because the judge sits in the agent's critical path on every action.

## Run it
```bash
git clone <this repo> && cd agent-action-guardrail
pip install -r requirements.txt
cp .env.example .env           # add your NEBIUS_API_KEY
export $(cat .env | xargs)
streamlit run app.py           # demo UI
pytest -q                      # offline tests (no key needed)
```
Without a key the app runs in rules-only mode; with a key the Nemotron judge is added as the 4th signal.

## Use it in your own agent
```python
from guardrail import GuardedExecutor, Action
g = GuardedExecutor(client=nemotron.get_client())
verdict, result, audit_hash = g.run(Action("send_email", {"to": "...", "body": "..."}, user_task="..."))
```

## Roadmap
XGBoost + SHAP classifier as a fifth signal, LangGraph `interrupt()` adapter, MCP server wrapper,
anchoring the audit head hash on Sepolia.

## License
MIT
