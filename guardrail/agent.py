from . import nemotron
from .models import Action


def plan(client, task: str, untrusted_context: str = "", agent_id="agent-1"):
    """Nemotron decides tool calls. `untrusted_context` (a web page / retrieved doc) is where
    prompt injections hide - the guardrail must catch what the agent is tricked into."""
    prompt = f"Task: {task}"
    if untrusted_context.strip():
        prompt += f"\n\nRetrieved document:\n{untrusted_context}"
    out = nemotron.chat_json(client, nemotron.PLANNER_SYSTEM, prompt)
    return [Action(c["tool"], c.get("args", {}), agent_id, task) for c in out.get("calls", [])]
