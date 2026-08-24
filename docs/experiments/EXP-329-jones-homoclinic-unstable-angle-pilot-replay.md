# EXP-329 — Printed-hub unstable-angle pilot replay

Status: frozen; not yet run

EXP-328 completed its integrations but wrote no receipt because its final
saddle-signature value remained a NumPy boolean. EXP-329 changes only that
value to a JSON-native boolean. All departure angles, eigenspace geometry,
radii, solver tolerances, horizons, minimum refinement, candidate thresholds,
execution gates, and claim limits are byte-for-byte equivalent in value.

As before, a pass validates the reference workflow rather than Jones's
homoclinic claim. Any sampled close return is only a refinement nomination;
the absence of one on 96 angles is not a rejection.

Manifest:
[`../../experiments/manifests/EXP-329-jones-homoclinic-unstable-angle-pilot-replay.json`](../../experiments/manifests/EXP-329-jones-homoclinic-unstable-angle-pilot-replay.json).
