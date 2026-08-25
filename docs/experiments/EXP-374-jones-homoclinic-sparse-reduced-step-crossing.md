# EXP-374 — Reduced-step sparse homoclinic crossing

Status: completed; failed prospectively frozen matching and termination gates

EXP-373 makes the physical projected arclength equation accurate but misses
the matching gate at its requested `Delta c=0.00015` step. EXP-374 retains its
qualified sources, 512-arc representation, full-state predictor, `(a,c)`
closing plane, common gauge, CSR/regularized-LSMR solve, unit closing-equation
weight, bounds, 40-evaluation budget, and all acceptance thresholds. Only the
desired `c` increment is halved to `7.5e-5`.

From EXP-368, the qualified local slope projects the exact `a=0.1798` crossing
after `Delta c=5.37476e-5`. The reduced step is therefore still a prospective
crossing attempt, not a retreat to another above-section point.

A pass below `a=0.1798` forms a qualified branch bracket. It does not itself
solve the exact historical section or establish uniqueness or computer-
assisted existence.

Manifest:
[`../../experiments/manifests/EXP-374-jones-homoclinic-sparse-reduced-step-crossing.json`](../../experiments/manifests/EXP-374-jones-homoclinic-sparse-reduced-step-crossing.json).

## Result

The reduced predictor lowers the initial maximum defect from EXP-373's
`2.99550e-3` to `1.18019e-3`. At the 40-evaluation cap, EXP-374 reaches
`(a,c)=(0.1798177058402,10.3171885556579)`, maximum matching defect
`5.26837e-6`, and projected arclength residual `-1.78479e-9`. Step reduction
therefore improves the controlling defect by a factor of `2.16` and preserves
the plane gate, but it does not qualify a root and the final `a` remains above
the historical section.

The normalized node displacement is `0.12472`, roughly half EXP-373's value,
with ample node and global-bound margins. This exact-node state is a justified
warm-correction seed on the same frozen plane; it is not a bracket endpoint.

Raw receipt: `artifacts/EXP-374/receipt.json`, 85,695 bytes, SHA-256
`eb33dd814da0c50fa82c4e4c3e111aaba5246ae87266056326dc9c9ccad2d760`.
