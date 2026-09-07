#!/usr/bin/env python3
"""Read-only analytic reproducer of a legacy turning-point helper limitation."""
import hashlib
import json
from pathlib import Path

from butterfly.return_map import _critical_points


class StationaryInflection:
    def __call__(self, x):
        return (x-.5)**3

    def derivative(self):
        return lambda x: 3*(x-.5)**2


def main():
    source = Path(__file__).resolve().parents[1] / "python/butterfly/return_map.py"
    result = {"kind": "analytic-legacy-stationary-inflection-reproducer",
        "legacy_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "function": "(x-0.5)^3", "derivative": "3*(x-0.5)^2", "domain": [0., 1.],
        "grid_size": 4097, "minimum_prominence": .03, "true_turning_points": [],
        "legacy_reported_points": list(_critical_points(StationaryInflection(), grid_size=4097, minimum_prominence=.03)),
        "target_trajectories": 0, "historical_rossler_impact": "not evaluated"}
    result["legacy_defect_reproduced"] = result["legacy_reported_points"] != result["true_turning_points"]
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
