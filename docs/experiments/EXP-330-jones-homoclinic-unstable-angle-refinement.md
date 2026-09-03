# EXP-330 — Printed-hub unstable-angle refinement

Status: preserved administrative failure; no numerical rows executed

EXP-329 completed all 96 departures but nominated no return. Its closest
sample, angle `4.352414822160859`, came within `0.01047463129580855` of the
small equilibrium. That is just outside the `0.01` distance gate, but the
displacement was `0.9992900383572414` transverse to the stable eigendirection,
so distance alone would be misleading.

EXP-330 binds the raw EXP-329 receipt by SHA-256 and freezes 257 equally spaced
angles centered on that prospectively selected sample. The window extends one
complete EXP-329 grid spacing (`2*pi/96`) to either side and includes the
source angle exactly. Every integration, return horizon, time-minimum
refinement, and candidate threshold is unchanged.

A candidate must pass both gates: distance at most `0.01` and stable transverse
ratio at most `0.1`. A run pass validates only receipt binding, complete
coverage, and finite observables. A nominated angle would still require a
multiple-shooting or collocation boundary-value solve; no nomination on this
finite interval would not reject a homoclinic orbit elsewhere.

Manifest:
[`../../experiments/manifests/EXP-330-jones-homoclinic-unstable-angle-refinement.json`](../../experiments/manifests/EXP-330-jones-homoclinic-unstable-angle-refinement.json).

The clean committed run stopped at module import before reading the manifest or
launching a worker: direct file execution could not resolve the package-style
`scripts.scan_jones_homoclinic_unstable_angles` import. No receipt was written
and no scientific inference follows. EXP-331 preserves every scientific value
and adds only a direct-execution import fallback.
