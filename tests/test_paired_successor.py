"""A named, prospectively reviewed successor is not a retry of EXP-481."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

from butterfly.paired_campaign import planned_seeds, trial_grid
from butterfly.paired_release import decision_context, experiment_paths

ROOT = Path(__file__).resolve().parents[1]


def test_successor_changes_only_declared_numerical_resource_and_random_draw_fields():
    old = json.loads((ROOT/experiment_paths("EXP-481")["plan"]).read_bytes())
    new = json.loads((ROOT/experiment_paths("EXP-482")["plan"]).read_bytes())
    assert new["seeds"]["ordered_table_sha256"] == "35efa7ac23f569382938dddd4643a7b0b379c4b22f51d5d09eadabdd8362efdf"
    old_seeds, new_seeds = planned_seeds(old), planned_seeds(new)
    assert not set(map(tuple,old_seeds["xz"])) & set(map(tuple,new_seeds["xz"]))
    old["experiment_id"] = "EXP-482"
    old["seeds"].update(random_seed=482001,ordered_table_sha256=new["seeds"]["ordered_table_sha256"])
    old["analysis"]["options"]["random_seed"] = 482002
    old["collection"].update(profiles=[dict(name="rk4-00025",dt=.0025),dict(name="rk4-000125",dt=.00125)],
        batch_size=512,maximum_events_per_batch=262144,maximum_steps_per_batch=240000)
    old["resources"]["supervisor_poll_seconds"] = 1
    assert new == old
    grid = trial_grid(new)
    assert sum(t.stage=="qualification" for t in grid) == 128
    assert sum(t.stage=="collection" for t in grid) == 64
    assert new["collection"]["maximum_events_per_batch"]//512 == 512


def test_fixed_successor_roles_do_not_alias_old_attempt_or_review():
    first, second = experiment_paths("EXP-481"), experiment_paths("EXP-482")
    assert set(first.values()).isdisjoint(second.values())
    assert second["slot"] == "artifacts/EXP-482/target-once.json"
    assert decision_context(dict(experiment_id="EXP-482"),"a"*64).startswith("# EXP-482 decision context\n")
    for value in ("EXP-483", "../EXP-481", "EXP-481/", None):
        with pytest.raises(ValueError): experiment_paths(value)


def test_unknown_experiment_cli_rejected_without_creating_any_output(tmp_path):
    output = tmp_path/"must-not-exist"
    result = subprocess.run([sys.executable,"-B",str(ROOT/"scripts/run_paired_campaign.py"),
        "--mode","control","--experiment-id","EXP-483","--output-dir",str(output)],
        capture_output=True,text=True,timeout=10)
    assert result.returncode != 0 and "invalid choice" in result.stderr
    assert not output.exists()
