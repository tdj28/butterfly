# EXP-380 — Failure-safe collocation replay

Status: frozen; not yet run

EXP-379 returns from adaptive collocation but loses its result when the
independent Radau replay raises on step-size collapse. EXP-380 repeats the
identical source bindings, initial mesh, BVP, derivatives, solver settings,
tolerances, node ceiling, replay, and scientific gates. Only the post-solve
audit behavior changes: a failed replay records its segment and message and
sets the unchanged replay gate false.

No replay failure can pass. The purpose is to preserve enough diagnostics to
decide whether the collocation solve failed, escaped the source-centered
domain, or produced a candidate requiring a different replay representation.

Manifest:
[`../../experiments/manifests/EXP-380-jones-homoclinic-collocation-failure-safe-replay.json`](../../experiments/manifests/EXP-380-jones-homoclinic-collocation-failure-safe-replay.json).
