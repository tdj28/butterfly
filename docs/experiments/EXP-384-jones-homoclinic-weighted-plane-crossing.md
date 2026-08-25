# EXP-384 — Weighted-plane homoclinic section crossing

Status: frozen; not yet executed

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
