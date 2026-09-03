# EXP-384 — Weighted-plane homoclinic section crossing

Status: attempted; administrative pre-solve bounds abort

EXP-383 passes the zero-step prerequisite for the prospectively weighted
hybrid plane.  EXP-384 retains the same 512-arc bounded multiple-shooting
system, analytic sensitivities, CSR/LSMR solver, weights, source receipts,
manifold construction, Radau tolerances, and `1e-8` root gate.  It changes only
the continuation step and the applicable direction/section gates.

The desired increment is `Delta c=7.5e-5`.  Every qualified local secant
predicts that step below exact `a=0.1798`.  EXP-383's corrected 512-arc nodes
are bound as the warm start, but the closing plane is centered at the new
full-state predictor.  A result must move forward from EXP-368 and finish at
or below `a=0.1798`; a sub-gate wrong-side root cannot pass.

Manifest:
[`../../experiments/manifests/EXP-384-jones-homoclinic-weighted-plane-crossing.json`](../../experiments/manifests/EXP-384-jones-homoclinic-weighted-plane-crossing.json).

A pass would qualify a bracket of the historical fixed-`a` section between
EXP-368 and EXP-384.  It would not yet qualify the exact fixed-`a` root,
uniqueness, a computer-assisted proof, or the full parameter-plane mechanism.

## Result

No orbit or optimizer evaluation ran.  The exact EXP-383 warm start has
`c-current_c=1.68723e-9`, while EXP-384's prospective optimizer floor requires
at least `1e-6`.  The runner correctly rejects that initial point as outside
the frozen bounds before constructing a scientific result.  This is an
administrative protocol incompatibility, not evidence about the weighted
plane or homoclinic branch.

EXP-385 removes only the optimizer lower wall.  It retains the final
forward-`c` check, the `a<=0.1798` section gate, the exact warm start, and every
root, arclength, and margin threshold.
