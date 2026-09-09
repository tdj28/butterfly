"""Derived public-release safety checks; no new numerical trajectories."""
import io
import json
import tarfile

import pytest
from scripts import release_exp496_contact_endpoint as release
from scripts import plot_exp496_contact_endpoint as plot


@pytest.mark.parametrize("name", ["../data", "/tmp/file", ".", "..", "a/b", "a\\b", "", "a\nb", "-option"])
def test_release_rejects_nonflat_or_unsafe_names(name):
    with pytest.raises(ValueError): release.safe_leaf(name)


def test_release_accepts_actual_profile_leaf():
    name = "local-a025-c083--region-1--depth-4--direction-0--candidate-0--DOP853--newton-0.npz"
    assert release.safe_leaf(name) == name


def test_release_and_plot_anchor_rejection_precedes_output(tmp_path):
    path = tmp_path/"data.json"
    path.write_text("{}")
    for function in (release.unpack, plot.build):
        output = tmp_path/function.__name__
        with pytest.raises(ValueError, match="anchor"):
            function(path, "0"*64, output)
        assert not output.exists()


def test_figure_rejects_missing_ledger_without_target_results():
    with pytest.raises(ValueError, match="ledger"):
        plot.validate(dict(passed=True, experiment_id="EXP-496", ledger=[], candidates=[]))


@pytest.mark.parametrize("fault", ["member-name", "symlink", "duplicate", "wrong-bytes", "shard-hash"])
def test_bound_archive_still_rejects_unsafe_or_changed_content(tmp_path, fault):
    tarpath = tmp_path/"part.tar"
    name = "extra.json" if fault == "member-name" else "summary.json"
    with tarfile.open(tarpath, "x") as archive:
        info = tarfile.TarInfo(name)
        info.size = 1
        if fault == "symlink":
            info.type, info.linkname, info.size = tarfile.SYMTYPE, "../outside", 0
            archive.addfile(info)
        else:
            archive.addfile(info, io.BytesIO(b"x"))
    member = dict(path="summary.json", bytes=1,
                  sha256=release.hashlib.sha256(b"y" if fault == "wrong-bytes" else b"x").hexdigest())
    members = [member, member] if fault == "duplicate" else [member]
    index = dict(schema="butterfly.exp496-full-data.v1", experiment_id="EXP-496",
        total_members=len(members), total_bytes=max(1, sum(m["bytes"] for m in members)),
        summary_sha256="0"*64, shards=[dict(path="part.tar", bytes=tarpath.stat().st_size,
            sha256="0"*64 if fault == "shard-hash" else release.sha256(tarpath), members=members)])
    path = tmp_path/"index.json"
    path.write_text(json.dumps(index))
    with pytest.raises(ValueError):
        release.unpack(path, release.sha256(path), tmp_path/"output")
    assert not (tmp_path/"outside").exists()
