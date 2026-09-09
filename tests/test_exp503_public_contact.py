"""Outcome-free public-replay interface tests; receipt tests follow release."""
import subprocess
import sys

import pytest
from scripts import verify_exp503_public_contact as public


def test_hash_refusal_precedes_plan_or_data_access(tmp_path,monkeypatch):
    path = tmp_path/"untrusted.json"
    public.run.write_json(path,{})
    monkeypatch.setattr(public.continuation,"PLAN",tmp_path/"missing-plan.json")
    with pytest.raises(ValueError,match="receipt hash"):
        public.verify(path,"0"*64)


def test_public_cli_documents_limited_scope():
    result = subprocess.run([sys.executable,"-m","scripts.verify_exp503_public_contact","--help"],
        capture_output=True,text=True,check=True)
    assert "not the full raw-data audit" in result.stdout
    assert "--expected-sha256" in result.stdout
