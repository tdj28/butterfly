# EXP-345 — Radius-0.02 Radau homoclinic persistence

Status: frozen; not yet run

EXP-344 qualifies persistence of the Radau root from matching radius `0.03` to
`0.025`. EXP-345 binds its exact 32 matched nodes and changes only the
nonlinear stable-manifold target radius to `0.02`.

The corrected nuisance gauge, global `a` box, Radau settings, 40-evaluation
budget, and `1e-8` maximum arc-defect threshold remain fixed. The parameter may
move by at most `2e-6`; angle and time retain their deliberately wider
nuisance-coordinate limits.

Passing creates a three-radius numerical root sequence. Continuation is still
required for a bounded uniqueness statement, and the result cannot validate
Jones's printed `a=0.1798` if the persistent root remains near `0.1826436`.

Manifest:
[`../../experiments/manifests/EXP-345-jones-homoclinic-radius020-radau.json`](../../experiments/manifests/EXP-345-jones-homoclinic-radius020-radau.json).
