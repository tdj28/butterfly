import copy
import json
import numpy as np
import pytest

from scripts.qualify_paired_sampling import PLAN, build_tables


def test_batch_table_independently_covers_every_seed_once_per_case_profile():
    table, rows = build_tables(json.loads(PLAN.read_bytes()))
    assert len(rows) == 512 and table["holdout"].sum() == 4096
    groups = {(r["candidate_id"], r["profile"]) for r in rows}
    assert len(groups) == 4
    for key in groups:
        coverage = np.zeros(8192, int)
        for row in rows:
            if (row["candidate_id"], row["profile"]) == key:
                lo, hi = row["global_seed_start"], row["global_seed_stop_exclusive"]
                coverage[lo:hi] += 1
                assert hi-lo == 64
                assert np.all(table["holdout"][lo:hi] == (row["split"] == "holdout"))
                assert not {"result", "passed", "word", "branch_count"} & set(row)
        assert (coverage == 1).all()


@pytest.mark.parametrize("key", ["permission", "range", "holdout", "hash", "profile"])
def test_unreviewed_plan_cannot_silently_change_declared_table(key):
    plan = copy.deepcopy(json.loads(PLAN.read_bytes()))
    if key == "permission":
        plan["execution_authorized"] = True
    elif key == "range":
        plan["seeds"]["xz_ranges"][0][0] = -100
    elif key == "holdout":
        plan["seeds"]["holdout_ids"][0] = 2048
    elif key == "profile":
        plan["collection"]["profiles"][0]["dt"] = .02
    else:
        plan["seeds"]["ordered_table_sha256"] = "0"*64
    with pytest.raises(ValueError):
        build_tables(plan)
