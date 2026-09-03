# EXP-344 — Radius-0.025 nuisance-gauge validation

Status: passed; first shrinking-radius persistence step qualified

EXP-343 solves the radius-`0.025` matching equations below `1e-8` and preserves
`a` to `1.30e-13`, but fails because its nearly null departure-angle coordinate
lands on the old box boundary. EXP-344 binds those exact matched nodes and does
not optimize them further.

Only the angle half-width is prospectively widened from `0.0327249` to `0.15`.
The physical endpoint geometry, radius, 32 Radau arcs, `a` box, residual gate,
and `2e-6` parameter-persistence requirement remain fixed. The one-evaluation
run passes only if the bound seed reproduces below `1e-8` and is interior under
the corrected nuisance gauge.

Passing qualifies one shrinking-radius persistence step. It does not replace
the radius-`0.02` test, validate the paper's printed `a`, or establish
uniqueness.

Manifest:
[`../../experiments/manifests/EXP-344-jones-homoclinic-radius025-gauge-validation.json`](../../experiments/manifests/EXP-344-jones-homoclinic-radius025-gauge-validation.json).

## Result

The bound seed reproduces exactly at maximum block defect `5.49708e-9`. Its
minimum normalized boundary margin is now `0.62557`, and all prospective gates
pass without another optimization step. The parameter remains
`a=0.18264360817415815`, only `1.30e-13` from the radius-`0.03` result.

This qualifies persistence from radius `0.03` to `0.025`. Radius `0.02` and
continuation are still required before treating the connection as fully
qualified or making any bounded uniqueness statement.

Tracked summary: [`receipts/EXP-344.json`](receipts/EXP-344.json). Raw receipt
SHA-256: `5f237112ec9f5c213942e5dc3f3b671282dda0e6f28935acc9caa50c2a8bd507`.
