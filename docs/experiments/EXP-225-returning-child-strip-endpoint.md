# EXP-225 — Returning-child strip endpoint successor

Status: frozen — awaiting execution

EXP-224 reaches its scalar root stage but aborts without a receipt when the
independent Radau child corrector only `5e-5` below the root terminates by
`xtol` without meeting the frozen correction criterion. EXP-225 changes only
that bilateral diagnostic distance to `1.5e-4`, where the primitive child has
larger separation from its parent. All root, orbit, stability, identity,
proper-subperiod, cross-solver, double-cover, and multiplier-square thresholds
are unchanged.

The runner now records child-qualification exceptions as explicit failed
controls. A pass has the same bounded meaning as EXP-224: a second period-6
flip crossing bounds the sampled child strip on this exact one-dimensional
offset path, without proving a global sheet endpoint or shrimp-boundary
connectivity.

Manifest:
[`../../experiments/manifests/EXP-225-returning-child-strip-endpoint.json`](../../experiments/manifests/EXP-225-returning-child-strip-endpoint.json).
