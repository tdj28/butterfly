from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.refine_jones_period6_flip_edges import SCHEMA


def test_flip_refinement_schema_is_versioned():
    assert SCHEMA == "butterfly.jones-period6-flip-refinement-manifest.v1"


def test_flip_refinement_direct_entrypoint_imports():
    script = Path(__file__).parents[1] / "scripts" / "refine_jones_period6_flip_edges.py"
    completed = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True,
        check=False,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
