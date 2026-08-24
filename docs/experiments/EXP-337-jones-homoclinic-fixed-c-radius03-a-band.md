# EXP-337 — Fixed-c radius-0.03 a-band

Status: passed; smooth single-shooting seed nominated

EXP-336 preserves a sole coverage failure on its broad `a` domain, while its
completed rows localize a `0.00034435` chord near miss at `a=0.1828`. EXP-337
binds the exact failed receipt and failure pattern. It does not reclassify or
relax EXP-336.

The successor restricts the new scan to the observed returning band
`a in [0.1803,0.1838]`, halves spacing to `0.00025`, and enlarges the
matching sphere from `0.025` to `0.03` to improve continuous return coverage.
The fixed printed `c`, 192 angles, nonlinear stable targets, solver, horizon,
ten-percent chord gate, winding calculation, and one-time-unit continuity gate
are unchanged in meaning.

A pass requires at least 15% inward-return coverage. A continuous nonzero-
degree cell remains only a coupled-root nomination; direct proximity alone is
not sufficient.

Manifest:
[`../../experiments/manifests/EXP-337-jones-homoclinic-fixed-c-radius03-a-band.json`](../../experiments/manifests/EXP-337-jones-homoclinic-fixed-c-radius03-a-band.json).

The 2,880-row successor completes in `308.881` seconds and passes all source,
geometry, event, finite-value, and coverage gates. Its 544 inward returns give
`0.18889` coverage. Thirty-two rows meet the direct chord gate.

The closest row lies at `a=0.18255`, angle `2.4707317223544725`, with chord
`0.00016226246805430567`. Its tangent residual is
`(-1.3773e-6,1.62256e-4)`. Both coarse hull cells remain degree zero, so the
first-return grid nominates no root cell. The closest row instead seeds
EXP-338's smooth angle--`a`--flight-time shooting solve, which removes event
selection from the residual.

Tracked summary: [`receipts/EXP-337.json`](receipts/EXP-337.json). Raw receipt
SHA-256: `dda7b03c5801054bb53b8df035f44a8c3c89c25ff97a6c8bb4585dfed27eb1ce`.
