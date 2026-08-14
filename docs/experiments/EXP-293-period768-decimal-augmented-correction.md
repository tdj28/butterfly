# EXP-293 — Augmented high-precision correction of the seventh-event candidate

Status: completed — failed `a_bounds` and source-neighborhood gates

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

## Result

The 1,024-step discrete augmented system converges in five Newton updates.
Maximum orbit and antiperiodic-tangent residuals fall to `2.75e-31` and
`1.23e-30`; phase and normalization residuals are `2.21e-52` and `1.90e-39`.
Half-orbit node RMS remains `2.58e-5`, comfortably above the `2e-6` gate, so
the solution does not collapse to the period-384 double cover.

Two gates fail. The corrected coordinate is
`a=0.2407010036753399572554819410`, displaced `-4.50e-9` from the Float64
candidate and outside the untouched bracket. The maximum tangent-node
displacement is `4.16 > 0.1`; this maximum occurs along a tangent field whose
source magnitude reaches `48.25`, while the normalized base tangent changes
only `2.24e-4` and the global source/corrected tangent cosine is `0.99724`.
The state and period displacements, `4.80e-5` and `1.40e-5`, pass their gates.

EXP-293 therefore validates the augmented formulation and excludes the former
double-cover failure mode at this discretization, but it does not restore the
seventh event. The result is consistent with fourth-order truncation dominating
the extremely narrow event bracket. A prospectively frozen multi-resolution
refinement must test that interpretation without changing these gates.

Raw receipt: `artifacts/EXP-293/receipt.json`, 353,475 bytes, SHA-256
`67bde56cc9dea819a105757157129a9279b8d1ce837ed7cd4ee713aa2e6ddc08`.
Compact receipt:
[`receipts/EXP-293.json`](receipts/EXP-293.json).
