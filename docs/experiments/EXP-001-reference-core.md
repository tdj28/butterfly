# EXP-001 — Reference numerical core

Status: exploratory implementation verification
Date: 2026-08-06
Claim targets: CLM-002 and infrastructure prerequisites for CLM-001

## Purpose

Establish a readable Float64 correctness path for the Rössler equations before
implementing event detection, classification, scanning, or GPU acceleration.

## Frozen inputs

- Equations: `x'=-y-z`, `y'=x+a*y`, `z'=b+z*(x-c)`.
- Proposed hub coordinate: `(a,b,c)=(0.1798,0.2,10.3084)`.
- Reference solver: SciPy DOP853, `rtol=1e-10`, `atol=1e-12`,
  `max_step=0.05` for the receipt integration.
- Verification trajectory: `(x,y,z)=(0,4,0)`, `t in [0,10]`.

## Acceptance checks

1. Analytic Jacobian matches a central finite difference.
2. Both analytic equilibria are zeros of the vector field.
3. The small equilibrium has the reported saddle-focus eigenstructure.
4. An equilibrium remains invariant under numerical integration.
5. A short nontrivial trajectory converges under tighter tolerances.

## Execution

```sh
uv sync --extra dev
.venv/bin/pytest
.venv/bin/butterfly verify
```

Observed environment: Python 3.12.13, NumPy 2.5.1, SciPy 1.18.0 on arm64
macOS. Result: 8 tests passed. The receipt reproduced the small-equilibrium
eigenvalues
`0.0889667722 +/- 0.9959555077 i` and `-10.3030439458`.

## Interpretation boundary

This verifies CLM-002 at the proposed coordinate and establishes the reference
model/integrator primitives. It does not yet reproduce a periodicity map,
classify a fundamental period, validate a Poincaré section, or establish any
global bifurcation/topological claim.
