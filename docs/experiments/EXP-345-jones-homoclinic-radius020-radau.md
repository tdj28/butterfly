# EXP-345 — Radius-0.02 Radau homoclinic persistence

Status: completed; preserved angle-boundary failure despite a sub-`1e-8`
match and invariant `a`

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

## Result

The radius-`0.02` solve reaches maximum block defect `5.60724e-9` and changes
`a` by only `4.34e-13`. It nevertheless drives the widened angle coordinate
exactly to its lower bound and exhausts 40 evaluations, so the
`optimizer_terminated_or_root_gate` check fails and the experiment remains
formally failed.

This is the same nuisance-gauge pathology isolated at radius `0.025`, not a
failure of the manifold match or parameter persistence. The failure-bound
successor will widen only that gauge and validate these exact nodes in one
evaluation, retaining the `1e-8` residual and `2e-6` `a` thresholds.

Tracked summary: [`receipts/EXP-345.json`](receipts/EXP-345.json). Raw receipt
SHA-256: `53fdbc103beccb03bd333070e76ee58f06d66629fc53a64253db44531e10995d`.
