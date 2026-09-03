from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "audit_segmented_floquet_precision.py"
SPEC = importlib.util.spec_from_file_location("segmented_floquet", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _roots(multiplier: complex, count: int) -> np.ndarray:
    radius = abs(multiplier) ** (1.0 / count)
    phase = np.angle(multiplier)
    return np.asarray(
        [
            radius * np.exp(1j * (phase + 2.0 * np.pi * index) / count)
            for index in range(count)
        ]
    )


def test_power_clustering_separates_equal_modulus_plus_and_minus_one():
    segment_count = 32
    roots = np.r_[
        _roots(-1e-90, segment_count),
        _roots(-1.0, segment_count),
        _roots(1.0, segment_count),
    ]
    roots = roots[np.random.default_rng(731).permutation(roots.size)]
    clusters = MODULE._balanced_power_clusters(roots, segment_count)
    recovered = sorted(
        [complex(np.median((cluster**segment_count).real)) for cluster in clusters],
        key=lambda value: value.real,
    )
    assert [cluster.size for cluster in clusters] == [segment_count] * 3
    assert np.allclose(recovered, [-1.0, 0.0, 1.0], atol=1e-12, rtol=0.0)


def test_power_clustering_retains_complex_conjugate_families():
    segment_count = 8
    roots = np.r_[
        _roots(1e-12, segment_count),
        _roots(0.7 + 0.2j, segment_count),
        _roots(0.7 - 0.2j, segment_count),
    ]
    clusters = MODULE._balanced_power_clusters(roots, segment_count)
    recovered = sorted(
        [np.mean(cluster**segment_count) for cluster in clusters],
        key=lambda value: value.imag,
    )
    assert np.allclose(recovered, [0.7 - 0.2j, 1e-12, 0.7 + 0.2j], atol=1e-12)
