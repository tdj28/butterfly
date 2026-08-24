# EXP-329 — Printed-hub unstable-angle pilot replay

Status: passed

EXP-328 completed its integrations but wrote no receipt because its final
saddle-signature value remained a NumPy boolean. EXP-329 changes only that
value to a JSON-native boolean. All departure angles, eigenspace geometry,
radii, solver tolerances, horizons, minimum refinement, candidate thresholds,
execution gates, and claim limits are byte-for-byte equivalent in value.

As before, a pass validates the reference workflow rather than Jones's
homoclinic claim. Any sampled close return is only a refinement nomination;
the absence of one on 96 angles is not a rejection.

All 96 departures and return integrations completed in `11.6161` seconds. No
angle passed the joint candidate gate. The closest trajectory, at angle
`4.352414822160859`, reached distance `0.01047463129580855`, narrowly outside
the `0.01` radius, but its displacement was `0.9992900383572414` transverse to
the stable eigendirection. The most stable-aligned sampled return was still
`0.9953544056007565` transverse and farther away at `0.02379150748340573`.
These data select the frozen EXP-330 local refinement; they do not reject the
homoclinic claim.

Tracked summary:
[`receipts/EXP-329.json`](receipts/EXP-329.json). Raw receipt SHA-256:
`ee7d0f82fba78a8334097ae1e5c14cd8fa533b5f38b08fc3594e4c340d7ddfea`.

Manifest:
[`../../experiments/manifests/EXP-329-jones-homoclinic-unstable-angle-pilot-replay.json`](../../experiments/manifests/EXP-329-jones-homoclinic-unstable-angle-pilot-replay.json).
