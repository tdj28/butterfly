# EXP-497: narrowing the qualified contact interval

Status: frozen and executing locally. Pre-outcome validation passed 2194 tests,
with one existing Linux-only skip; all sixteen actual analytic controls pass.
This continues the first-case endpoint lead from
[EXP-496](2026-09-09-exp496-contact-endpoint.md), now merged into main.

The local refinement is bounded to three new parameter values. Each requires
fresh DOP853/Radau primitive-cycle correction/observation and all four measured
fold representations, again in both solvers. The stopping target is the existing
full-state fixed-event input/next-return proximity criterion, not word matching.
The second case remains ineligible because its complete endpoint gate failed.

- [Prospective protocol](../experiments/EXP-497-contact-localization.md)
- [Machine plan](../../experiments/manifests/EXP-497-contact-localization.json)
- [Preflight and retained fixes](../experiments/EXP-497-preflight.md)

A successful point would locate an operational contact with one measured
right-hand fold. It would not yet establish a second critical point, C/D,
an invariant quotient, exact criticality or a source-matched Jones chain.
No paid review, GPU rental or restricted upload is involved. The pending
EXP-496 public-archive approval does not block this local calculation.

Execution source is `ec0bca1c35fd7ee34c99088dedd028cf4b4ca635`, pushed before
targets and preserved at `codex/exp497-local-execution`. The runtime checked
the live pushed SHA, clean source, input/import closure and disk reserve,
repeated its controls and created the exclusive consumed-attempt marker.
Evidence is retained at `artifacts/EXP-497/target-ec0bca1`; the witness is
`artifacts/EXP-497/target-once.json` and must not be reset.

At the current operational checkpoint, the first proposed parameter has both
periodic profiles and six of eight fold profiles recorded. The frozen numerical
source remains unchanged. No new contact verdict is interpreted before the
complete mesh, periodic-event, adaptive-ledger and scalar audit.
