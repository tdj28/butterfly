import json
from pathlib import Path

import pytest

from butterfly.scan import ScanManifest
from butterfly import tiles
from butterfly.tiles import (
    TileSpec,
    aggregate_scan_tiles,
    execute_scan_tile,
    verify_completed_aggregate,
    verify_completed_tile,
)


@pytest.fixture
def source_revision(monkeypatch):
    """Tile behavior tests must also run from source archives without .git."""
    values = {
        ("rev-parse", "HEAD"): "a" * 40,
        ("branch", "--show-current"): "test-branch",
        ("status", "--porcelain"): "",
    }
    monkeypatch.setattr(tiles, "git_value", lambda *arguments: values[arguments])


def tiled_manifest() -> dict:
    return {
        "schema": "butterfly.scan-manifest.v1",
        "experiment_id": "TEST-TILED-SCAN",
        "grid": {
            "a": {"min": 0.1798, "max": 0.1800, "count": 2},
            "b": 0.2,
            "c": {"min": 10.3084, "max": 10.31, "count": 2},
        },
        "integration": {
            "initial_state": [0.0, 4.0, 0.0],
            "transient": 1.0,
            "observation_horizon": 2.0,
            "max_crossings": 1,
            "solver": {
                "method": "DOP853",
                "rtol": 1e-9,
                "atol": 1e-11,
                "max_step": 0.1,
            },
        },
        "classifier": {
            "max_period": 2,
            "required_repeats": 2,
            "atol": 1e-6,
            "rtol": 1e-7,
        },
    }


def write_manifest(path: Path) -> Path:
    path.write_text(json.dumps(tiled_manifest()) + "\n", encoding="utf-8")
    return path


def test_tile_partition_is_exact_and_balanced() -> None:
    value = tiled_manifest()
    value["grid"]["c"]["count"] = 5
    manifest = ScanManifest.from_dict(value)
    specs = [TileSpec.for_manifest(manifest, index=index, count=3) for index in range(3)]
    indices = [point for spec in specs for point in spec.point_indices]
    assert indices == list(range(10))
    assert [len(spec.point_indices) for spec in specs] == [4, 3, 3]


def test_tiles_resume_and_aggregate_exact_grid(tmp_path: Path, source_revision) -> None:
    manifest_path = write_manifest(tmp_path / "manifest.json")
    output = tmp_path / "tiles"
    first = execute_scan_tile(
        manifest_path,
        output,
        tile_index=0,
        tile_count=2,
        require_clean=False,
    )
    resumed = execute_scan_tile(
        manifest_path,
        output,
        tile_index=0,
        tile_count=2,
        resume=True,
        require_clean=False,
    )
    assert resumed == first
    execute_scan_tile(
        manifest_path,
        output,
        tile_index=1,
        tile_count=2,
        require_clean=False,
    )
    aggregate = aggregate_scan_tiles(
        manifest_path, output, tile_count=2, require_clean=False
    )
    result = json.loads((output / "aggregate" / "result.json").read_bytes())
    assert aggregate["row_count"] == 4
    assert [row["point_index"] for row in result["rows"]] == [0, 1, 2, 3]
    assert len(set(aggregate["tile_ids"])) == 2
    assert aggregate_scan_tiles(
        manifest_path, output, tile_count=2, require_clean=False
    ) == aggregate
    assert verify_completed_aggregate(output / "aggregate") == aggregate


def test_resume_rejects_corrupted_completed_tile(tmp_path: Path, source_revision) -> None:
    manifest_path = write_manifest(tmp_path / "manifest.json")
    output = tmp_path / "tiles"
    execute_scan_tile(
        manifest_path,
        output,
        tile_index=0,
        tile_count=2,
        require_clean=False,
    )
    directory = output / "tile-00000-of-00002"
    result_path = directory / "result.json"
    result_path.write_bytes(result_path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="result hash mismatch"):
        verify_completed_tile(directory)


def test_resume_recovers_directory_with_only_temporary_file(tmp_path: Path, source_revision) -> None:
    manifest_path = write_manifest(tmp_path / "manifest.json")
    output = tmp_path / "tiles"
    directory = output / "tile-00000-of-00002"
    directory.mkdir(parents=True)
    (directory / ".result.json.tmp").write_text("interrupted", encoding="utf-8")
    receipt = execute_scan_tile(
        manifest_path,
        output,
        tile_index=0,
        tile_count=2,
        resume=True,
        require_clean=False,
    )
    assert receipt["row_count"] == 2
    verify_completed_tile(directory)


def test_tiled_scan_still_requires_real_git_provenance(monkeypatch):
    monkeypatch.setattr(tiles, "git_value", lambda *arguments: None)
    with pytest.raises(RuntimeError, match="require a Git source commit"):
        tiles._source(require_clean=False)


def test_tiled_scan_rejects_dirty_source_when_required(monkeypatch):
    def git_value(*arguments):
        return " M source.py" if arguments == ("status", "--porcelain") else "a" * 40

    monkeypatch.setattr(tiles, "git_value", git_value)
    with pytest.raises(RuntimeError, match="require a clean source tree"):
        tiles._source(require_clean=True)
