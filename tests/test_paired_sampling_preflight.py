import json

import pytest

from scripts import check_paired_sampling_preflight as preflight


@pytest.mark.parametrize("mutation", ["permission", "case", "review", "hash", "decisions"])
def test_draft_cannot_be_promoted_by_editing_a_flag(monkeypatch, mutation):
    plan = json.loads(preflight.PLAN.read_bytes())
    if mutation == "permission":
        plan["execution_authorized"] = True
    elif mutation == "case":
        plan["candidate_ids"].pop()
    elif mutation == "review":
        plan["review"] = {"approved": True}
    elif mutation == "hash":
        plan["inputs"]["candidates"]["sha256"] = "0"*64
    else:
        plan["decisions"] = {"pretend": "ready"}
    monkeypatch.setattr(preflight.evidence, "checked_input", lambda *a: pytest.fail("should reject before input access"))
    with pytest.raises(ValueError):
        preflight.prepare(plan)


def test_execute_cli_rejects_before_source_input_or_solver_access(monkeypatch):
    monkeypatch.setattr("sys.argv", ["preflight", "--mode", "execute", "--source-commit", "a"*40])
    monkeypatch.setattr(preflight.evidence, "source_binding", lambda *a: pytest.fail("source accessed"))
    monkeypatch.setattr(preflight, "prepare", lambda *a: pytest.fail("input accessed"))
    with pytest.raises(ValueError, match="target execution is unavailable"):
        preflight.main()
