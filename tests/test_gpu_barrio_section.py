import numpy as np

from scripts.qualify_gpu_barrio_section import normalized_critical_midpoints


def test_normalized_critical_midpoints_use_each_domain() -> None:
    partition = {"critical_point_intervals": [[2.0, 4.0], [6.0, 8.0]]}
    assert np.allclose(
        normalized_critical_midpoints(partition, (0.0, 10.0)),
        [0.3, 0.7],
    )
