#!/usr/bin/env python3
"""Verify a public core bundle, redraw its atlas, and reevaluate two candidates.

Only trusted scripts from this source checkout run; an archive supplies passive
JSON inputs. Numerical results are written to a new directory, never over
historical experiment receipts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys

try:
    from scripts.research_bundle import (
        canonical_json, check_replay_environment, extract_archive, file_sha256,
        source_revision, verify_bundle,
    )
except ModuleNotFoundError:
    from research_bundle import (
        canonical_json, check_replay_environment, extract_archive, file_sha256,
        source_revision, verify_bundle,
    )


def render_atlas(bundle_dir: Path, output: Path) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import BoundaryNorm, ListedColormap
    from matplotlib.patches import Patch
    import numpy as np
    from butterfly.plotting import parameter_plane, pixel_edges
    try:
        from scripts.animate_ac_atlas import colors
    except ModuleNotFoundError:
        from animate_ac_atlas import colors

    data_path = bundle_dir / "artifacts/EXP-021/frame-005.json"
    receipt = json.loads((bundle_dir / "artifacts/EXP-021/frame-005.receipt.json").read_bytes())
    manifest = bundle_dir / "experiments/manifests/EXP-021-multi-b-ac-atlas.json"
    if receipt.get("result_sha256") != file_sha256(data_path) or receipt.get("manifest_sha256") != file_sha256(manifest) or receipt.get("complete") is not True:
        raise ValueError("historical atlas frame/manifest receipt binding failed")
    frame = json.loads(data_path.read_bytes())
    plane = parameter_plane(frame)
    cmap, norm = colors(32)
    fig, axis = plt.subplots(figsize=(8.1, 6.0), constrained_layout=True)
    axis.imshow(
        plane.values, origin="lower", interpolation="nearest", aspect="auto",
        extent=(*pixel_edges(plane.a_values), *pixel_edges(plane.c_values)), cmap=cmap, norm=norm,
    )
    axis.set(xlabel=r"$a$", ylabel=r"$c$", title=r"Archived Rössler recurrence atlas, $b=0.2$")
    axis.set_xlim(float(plane.a_values[0]), float(plane.a_values[-1]))
    axis.set_ylim(float(plane.c_values[0]), float(plane.c_values[-1]))
    # The map also has special-status colors. A separate periodic mappable
    # keeps unresolved/escaping/chaotic codes out of the period colorbar.
    last_period = max(plane.periods_present)
    period_cmap = ListedColormap([cmap(norm(period)) for period in range(1, last_period + 1)])
    period_norm = BoundaryNorm(np.arange(0.5, last_period + 1.5), period_cmap.N)
    colorbar = fig.colorbar(ScalarMappable(norm=period_norm, cmap=period_cmap), ax=axis, ticks=list(plane.periods_present), fraction=0.045, pad=0.03)
    colorbar.set_label("Detected recurrence period")
    palette = {"escaping": "#ffffff", "unresolved": "#d9d9d9", "numerical_failure": "#7f0000"}
    axis.legend(handles=[Patch(facecolor=palette[label], edgecolor="#555555", label=label.replace("_", " ")) for label in plane.labels_present if label in palette], loc="upper right", fontsize=8)
    fig.savefig(output, dpi=180)
    plt.close(fig)
    return {
        "schema": "butterfly.core-atlas-rerender.v1",
        "operation": "cached_classification_rerender",
        "new_trajectory_integration": False,
        "source_frame_sha256": file_sha256(data_path),
        "historical_source_commit": receipt["source_commit"],
        "point_count": len(frame["rows"]),
        "label_counts": receipt["label_counts"],
        "figure": {"path": output.name, "sha256": file_sha256(output), "bytes": output.stat().st_size},
        "claim_scope": "Redraws archived classifications only. Unresolved does not mean chaotic; this is not a new atlas integration.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--archive", type=Path)
    inputs.add_argument("--bundle-dir", type=Path, help="previously verified extracted core bundle")
    parser.add_argument("--sha256", help="required with --archive; release archive checksum")
    parser.add_argument("--output-dir", type=Path, required=True, help="new directory; existing paths are refused")
    args = parser.parse_args()
    if args.archive is not None and not args.sha256:
        parser.error("--archive requires --sha256 from the release")
    if args.bundle_dir is not None and args.sha256:
        parser.error("--sha256 applies only to --archive")
    output = args.output_dir.resolve()
    if args.output_dir.exists() or args.output_dir.is_symlink():
        raise FileExistsError(f"refusing to overwrite: {args.output_dir}")
    root = Path(__file__).resolve().parents[1]
    if args.archive is not None:
        bundle_dir = output / "data"
        index = extract_archive(args.archive, bundle_dir, expected_sha256=args.sha256)
    else:
        bundle_dir = args.bundle_dir.resolve()
        index = verify_bundle(bundle_dir)
        if bundle_dir == output or bundle_dir in output.parents:
            raise ValueError("replay output must not be inside the input bundle")
    check_replay_environment(bundle_dir, root)
    output.mkdir(parents=True, exist_ok=True)
    atlas = render_atlas(bundle_dir, output / "atlas-b020.png")
    (output / "atlas.receipt.json").write_bytes(canonical_json(atlas))
    print("Atlas redrawn from archived classifications; reevaluating flip and homoclinic candidates.", flush=True)
    completed = subprocess.run([
        sys.executable, str(root / "scripts/replay_core_numerics.py"),
        "--bundle-dir", str(bundle_dir), "--output-dir", str(output / "numerics"),
    ], cwd=root, check=False)
    receipt = {
        "schema": "butterfly.core-replay-summary.v1",
        "bundle_id": index["bundle_id"],
        "bundle_source": index["source"],
        "replay_source": source_revision(root, allow_dirty=True),
        "python": platform.python_version(),
        "atlas": atlas,
        "numerical_returncode": completed.returncode,
        "passed": completed.returncode == 0,
        "claim_scope": "Core candidate reevaluation plus cached atlas rendering, not full discovery reproduction or independent existence validation.",
    }
    (output / "replay.receipt.json").write_bytes(canonical_json(receipt))
    print(json.dumps({"passed": receipt["passed"], "output_dir": str(output)}, indent=2))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
