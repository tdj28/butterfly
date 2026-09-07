# Both nominated cycles pass the paired-section check

EXP-480 completed: **both cases qualified under all four solver profiles**.
It took 32.28 seconds on the local CPU, with no retries. The raw file audit
passed, and a verified 12.35 MB data backup is stored on prax. The exact
execution source is preserved at remote `codex/exp480-execution`.

The result reproduces six historical-section versus eight Barrio-section
returns on each cycle. Solver differences are comfortably inside the fixed
gates, and the new half-plane uncertainty check also passes. See the
[illustrated experiment record](../experiments/EXP-480-paired-section-reproducibility.md)
for the figure, numbers, raw hashes, backup location and reproduction command.

This is good numerical groundwork for Jones's symbolic test, not confirmation
of the chain. No partition, critical letter, word or arrow was inferred. The
next implementation is the
[common-population transient collector](../experiments/EXP-481-common-population-partition-design.md):
both sections on the same trajectories, explicit capture conditioning,
trajectory-level uncertainty and controlled event weighting.
