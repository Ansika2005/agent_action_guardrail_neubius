import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from guardrail import GuardedExecutor
from guardrail.scenarios import SCENARIOS
from guardrail.nemotron import extract_json


def make(tmp_path):
    g = GuardedExecutor(client=None, audit_path=str(tmp_path / "a.jsonl"))
    for t in ("query_db", "send_email"):
        g.behavior.seed("agent-1", t, 10)
    return g


@pytest.mark.parametrize("name,action,expected", SCENARIOS)
def test_scenarios(tmp_path, name, action, expected):
    v, result, _ = make(tmp_path).run(action)
    assert v.decision == expected, (name, v)
    assert (result is not None) == (expected == "allow")


def test_audit_chain_detects_tampering(tmp_path):
    g = make(tmp_path)
    for _, a, _ in SCENARIOS[:3]:
        g.run(a)
    assert g.audit.verify()
    p = tmp_path / "a.jsonl"
    p.write_text(p.read_text().replace('"decision": "allow"', '"decision": "block"', 1))
    assert not g.audit.verify()


def test_extract_json_strips_reasoning():
    assert extract_json('<think>hmm {x}</think> {"risk": 0.2}') == {"risk": 0.2}
