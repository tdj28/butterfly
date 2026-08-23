# EXP-319 — Same-map high-precision switch to the immediate seventh daughter

Status: frozen; not yet run

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
