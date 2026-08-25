# EXP-380 — Failure-safe collocation replay

Status: completed; failed collocation, margins, section, and replay gates

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

## Result

The failure-safe receipt shows that collocation escapes the source-centered
neighborhood in two iterations. It stops at 1,537 mesh nodes with maximum RMS
residual `68.6584` and boundary residual `3.97962e-5`; the returned parameters
are `(a,c)=(0.28048693,10.44828266)`, angle `-130.14348`, and flight time
`194.23639`. All global margins and the node margin are strongly negative.
Independent replay then fails at segment 339 with Radau step-size collapse.

This is an unconstrained collocation-globalization failure, not a branch root
or negative evidence for Jones. The next protocol first asks collocation to
reproduce qualified EXP-368 on a zero-step physical plane, using a
deterministically subdivided 512-arc mesh. Only after that positive control
passes will collocation take small receipt-bound continuation steps.

Raw receipt: `artifacts/EXP-380/receipt.json`, 162,119 bytes, SHA-256
`4b59f6b9364f5996eb116e7c6fa17079c51c169b4658757af97473d7564ee842`.
