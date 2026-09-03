# EXP-328 — Printed-hub unstable-angle return pilot

Status: administrative failure — no receipt; EXP-329 frozen

CLM-003 remains the largest untested Jones claim: the reported hub coordinate
is said to be a saddle-focus homoclinic point. EXP-001 proves the local
saddle-focus eigenstructure, while EXP-155 proves only that the continued
finite-period orbit is not itself the homoclinic connection.

EXP-328 is the CPU reference stage for a global manifold search. At
`(a,b,c)=(0.1798,0.2,10.3084)`, it places 96 midpoint angles on a `1e-7`
circle in the analytic two-dimensional unstable eigenspace. Each trajectory
must exit a radius-`0.01` sphere, then is tracked for 400 more time units with
DOP853. Dense output refines its closest post-departure return to the small
equilibrium and measures transverse misalignment from the one-dimensional
stable eigendirection.

Execution coverage and finite observables determine pass/fail. A return within
`0.01` with stable transverse ratio below `0.1` is only nominated. A finite
angle grid can neither prove nor reject a homoclinic orbit; its purpose is to
calibrate horizons, return-distance scales, angular refinement, and a future
GPU parity contract.

Manifest:
[`../../experiments/manifests/EXP-328-jones-homoclinic-unstable-angle-pilot.json`](../../experiments/manifests/EXP-328-jones-homoclinic-unstable-angle-pilot.json).

## Administrative result

All 96 integrations completed in about 15 seconds, but serialization of the
final receipt stopped on a NumPy boolean in the saddle-signature check. No raw
receipt was written and no scientific classification is recoverable from
stdout. EXP-329 changes only that value to a JSON-native boolean and freezes an
otherwise identical replay. EXP-328 is not re-run or reclassified.
