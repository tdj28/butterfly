# FND-060 — The full-flow Floquet-zero center criterion is invalid

Status: mathematical interpretation corrected 2026-09-04; scalar-map
double-critical membership remains open. Frozen experiment records are retained.

EXP-188 resolves 289 period-6 orbit cells with closure below `5.19e-12`, fixing
EXP-187's immediate continuation-scale failure. The signed dominant transverse
multiplier diagnostic contains 65 adjacent sign crossings and 17 numerically
near-zero cells in the frozen neighborhood. These are diagnostic values, not
established zeros of continuously tracked Floquet eigenvalues.

One coarse stencil satisfies the four-sign-change saddle screen, but its fit
already misses the declared stationary-value and RMS gates. More importantly,
its fully resolved `5 x 5` refinement contains no stationary saddle candidate.
Coverage is `0.655329`, below `0.75`, so both the coarse and refinement gates
fail and independent Radau validation is never invoked.

The earlier explanation incorrectly applied the derivative-product formula
for a scalar map to the monodromy matrix of a smooth flow. For a regular
finite-period Rössler orbit, Liouville's formula gives

```text
det M(T) = exp(integral_0^T [a + x(t) - c] dt) > 0.
```

The autonomous neutral multiplier is one. Neither transverse multiplier can
therefore vanish exactly. A computed zero may reflect loss of numerical
precision; a sign change in the real part of the selected largest-modulus
eigenvalue can also occur through a complex pair or a change of selected mode.
It does not define a full-flow superstability curve. The formula and
invertibility are given in [Teschl, equation (3.122)](https://www.mat.univie.ac.at/~gerald/ftp/book-ode/ode.pdf).

This corrects our modern interpretation, not the Jones/Barrio claim about
critical membership in a scalar return-map representation. The next valid
test must define that representation, independently reconstruct its two
critical points, and test their separate memberships in the corrected orbit,
including section and projection dependence.

Evidence: [`../experiments/EXP-188-fine-jones-floquet-center-search.md`](../experiments/EXP-188-fine-jones-floquet-center-search.md).
