# EXP-319 — Same-map high-precision switch to the immediate seventh daughter

Status: passed — one-resolution supercritical nomination

EXP-318 resolves the tested period-768 parent and primitive period-1536
candidate as stable/stable. That rules out promoting the sampled pair as a
supercritical exchange, but it does not show whether the candidate is the
immediate daughter of the seventh event.

EXP-319 removes the mixed-representation ambiguity. It starts from EXP-295's
passed 4,096-step RK4 3/8 augmented period-768 event and evaluates the doubled
child with the identical 50-digit tableau and steps per segment. Both tangent
signs are corrected at predictor lengths `3.125e-5` and `6.25e-5` using cyclic
block elimination to a five-variable Newton system. All four children must
pass `1e-20` matching, phase, and pseudo-arclength gates, retain primitive
half-node separation, agree across tangent sign, open on one parameter side,
show parameter displacement proportional to amplitude squared, preserve
period doubling, and have the stability predicted by that branch side.

EXP-318 places the parent on the stable higher-`a` side. A primitive unstable
daughter opening toward higher `a` nominates a subcritical birth; a primitive
stable daughter opening toward lower `a` nominates a supercritical birth. A
mixed side, nonquadratic opening, neutral daughter, or same-side stability
contradiction fails without relaxation.

A pass is a one-resolution nomination only. Promotion requires an independently
frozen 8,192-step or algebraically distinct replication. It does not
retrospectively pass EXP-318 or establish global attraction, basin measure,
universality, TBA membership, homoclinic geometry, or full-plane topology.

Manifest:
[`../../experiments/manifests/EXP-319-jones-period1536-decimal-child-switch.json`](../../experiments/manifests/EXP-319-jones-period1536-decimal-child-switch.json).

## Result

All four corrections pass. At predictor length `3.125e-5`, both tangent signs
produce primitive half-node RMS near `7.88e-7`, lower-`a` displacements near
`1.292e-13`, and stable child moduli `0.982255/0.982282`. Doubling the
predictor produces half-node RMS near `1.577e-6`, lower-`a` displacements near
`5.171e-13`, and stable moduli `0.928772/0.928989`.

The fitted parameter-versus-amplitude exponent is `2.000728`, essentially the
quadratic opening required for a generic flip branch. Tangent-sign relative
spreads are only `0.00305` in displacement and `0.00152` in amplitude. Final
matching residuals are below `2.84e-21`; cyclic spectra agree at stored
precision and neutral residuals remain below `1.06e-18`.

Because the immediate stable daughter opens toward lower `a`, opposite
EXP-318's independently stable higher-`a` parent side, this nominates the
seventh birth as locally supercritical. It also shows that EXP-299's stable
higher-`a` candidate is not the immediate local daughter in this
representation. Promotion still requires the frozen 8,192-step replication.

Raw receipt: `artifacts/EXP-319/receipt.json`, 1,393,853 bytes, SHA-256
`6b9ca510a9f04c5a8964a04dffbaeb4471f9a760ddadde0a14a2208febd42c33`.
Compact receipt: [`receipts/EXP-319.json`](receipts/EXP-319.json).
