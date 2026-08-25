# EXP-360 — Pseudo-arclength receipt recovery

Status: passed

EXP-359 completes its numerical solve but loses the atomic receipt when
canonical JSON rejects NumPy boolean check values. EXP-360 repeats the exact
same source bindings, gauge alignment, 32-to-128 subdivision, tangent,
`Delta c=0.0005` predictor, two-parameter variational equations, solver,
bounds, budget, and acceptance thresholds.

Only the experiment identifier and conversion of terminal checks to native
JSON booleans change. A regression test binds that administrative correction.

Manifest:
[`../../experiments/manifests/EXP-360-jones-homoclinic-pseudoarclength-step1-receipt-recovery.json`](../../experiments/manifests/EXP-360-jones-homoclinic-pseudoarclength-step1-receipt-recovery.json).

The recovered run passes all ten frozen checks. The 128-arc Radau correction
lands at

`(a,c)=(0.18053212047071568,10.314886371675088)`

with maximum matching defect `6.7747229841834155e-9`, matching-residual norm
`1.2390073164106867e-8`, and pseudo-arclength residual
`-3.4267090033568426e-12`. The optimizer terminates by `gtol` in 35 function
evaluations. The node-boundary margin is `0.94488`; no guardrail is active.

The corrector realizes `97.27%` of the desired `Delta c=0.0005` predictor.
Its secant from EXP-350 is `da/dc=-0.3255435270`, preserving the earlier local
slope and linearly projecting `a=0.1798` near `c=10.3171352890`. Thus the
fixed-coordinate floor did not mark an immediate termination of the qualified
branch. A later fold remains possible, and the historical-path intersection,
uniqueness, and computer-assisted existence are still open.

Raw receipt: `artifacts/EXP-360/receipt.json`, 29,123 bytes, SHA-256
`d7f7231c2634fe07d334c77c2f9b66df09fca11443fa34d8bfdeb307686b5224`.
