# EXP-289 — Near-event period-1536 qualification

Status: completed — failed at the frozen criticality-resolution gate

EXP-288 nominates six primitive period-1536 candidates but their preliminary
long-product multipliers are representation-conditioned. EXP-289
prospectively selects the largest-predictor positive candidate because it has
the largest half-period separation and best direct closure/neutral residual of
that bilateral pair; its preliminary stability label is explicitly not part
of the selection rule.

DOP853 and Radau independently correct the 1,024-segment parent and
2,048-segment child at the candidate's common `a`. Both must agree on a
resolved parent/child stability exchange, retain solver node identity, child
half-period nonclosure, and exact `1792/2048` section identity, and pass the
unchanged `0.02` multiplier-spread gate. Either a consistent supercritical or
consistent subcritical result passes; a mixed, neutral, or otherwise
unresolved classification fails. This avoids encoding the desired Jones
outcome in the acceptance criterion.

Manifest:
[`../../experiments/manifests/EXP-289-jones-period1536-near-event-qualification.json`](../../experiments/manifests/EXP-289-jones-period1536-near-event-qualification.json).

## Result

Both solvers independently correct the same parent and child, and every
nonclassification gate passes. DOP853/Radau child multipliers are
`-1.1073340104/-1.1073276570`, so both classify the period-1536 child as
unstable; their relative modulus spread is only `5.74e-6`. The child retains
half-period closures `4.42e-6/4.66e-6`, exact `1792/2048` identity, and exact
cross-solver node agreement at the stored phases.

The frozen test nevertheless fails because the parent remains inside the
`1e-4` neutral margin: DOP853/Radau give moduli
`0.9999972557/1.0000021582`. Their relative spread is `4.90e-6`, but they
straddle one, so the criticality classification is `other-or-unresolved`.
This is strong evidence for an unstable child on the stable-parent side—that
is, a subcritical seventh birth—but it is not promoted. EXP-290 moves the
same child branch farther from the event before repeating the two-solver test.

Raw receipt: `artifacts/EXP-289/receipt.json`, 388,767 bytes, SHA-256
`546a199d1c3747d2eeaaa868f420c5bcc5ab3de9b8a3ab6a144e957d0a13f16c`.
Compact receipt:
[`receipts/EXP-289.json`](receipts/EXP-289.json).
