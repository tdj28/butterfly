"""Published result/figure closure; no new flow integrations."""
from copy import deepcopy
import json

import pytest

from scripts import plot_exp495_fold_cycle_membership as figure


def actual():
    return json.loads((figure.run.ROOT/"docs/experiments/receipts/EXP-495-fold-cycle-membership.json").read_bytes())


def test_complete_published_census():
    d = figure.derive(actual())
    assert len(d["rows"]) == 26
    assert sum(bool(r["variants"]) for r in d["rows"]) == 10
    assert sum(len(r["variants"])*6 for r in d["rows"]) == 240
    assert all(c["complete"] for c in d["cases"])


@pytest.mark.parametrize("kind", ["missing-failure", "invented-success", "changed-state", "changed-envelope"])
def test_figure_rejects_edited_evidence(kind):
    r = deepcopy(actual())
    if kind == "missing-failure":
        r["rows"].pop(0)
    elif kind == "invented-success":
        r["cases"][0]["status"] = "proximate-at-primary-radius"
    elif kind == "changed-state":
        next(v for v in r["rows"] if v["variants"])["variants"][0]["fold_input"][0] += 1.
    else:
        r["cases"][0]["envelope"]["minimum_state_distance"] = 0.
    with pytest.raises(ValueError):
        figure.derive(r)


def test_public_figure_receipts_and_bytes():
    figure.verify(figure.run.ROOT/"docs/figures")
