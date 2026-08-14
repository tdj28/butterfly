# EXP-293 — Augmented high-precision correction of the seventh-event candidate

Status: frozen before execution

EXP-292 shows that correcting only the orbit can converge toward a nearby
lower-period double cover. EXP-293 instead couples every period-768 orbit node
to an antiperiodic tangent node while solving for the period and `a` in
50-decimal-digit arithmetic. The tangent must return with the opposite sign,
so the period-384 double cover cannot satisfy the augmented boundary condition.

For each Newton update, exact first- and second-variational equations are
integrated with classical RK4 at 1,024 steps on each of 1,024 segments. Cyclic
block elimination reduces 6,146 matching unknowns to an 8-by-8 Decimal system
in the base state, base tangent, total period, and `a`. The frozen gates require
all augmented residuals below `1e-22`, `a` inside the untouched EXP-280
bracket, bounded source displacement, and half-orbit node RMS above `2e-6`.

A pass validates one discrete augmented formulation. It does not yet qualify
the seventh event: resolution convergence and an independent RK4 3/8 tableau
must agree before FND-101 can be superseded.

Manifest:
[`../../experiments/manifests/EXP-293-period768-decimal-augmented-correction.json`](../../experiments/manifests/EXP-293-period768-decimal-augmented-correction.json).
