# EXP-212 — Broad pseudo-arclength extension of the period-6 flip curve

Status: complete — failed symmetric range gate; upper extension passed

## Question

Does the EXP-206 period-6 flip segment extend as a regular orbit-defined curve
well beyond the `c=7.16--7.32` child-sheet patch?

## Frozen design

The two terminal pairs of EXP-206 seed independent upward and downward
pseudo-arclength traces at fixed `b=0.2`. Each corrector uses an exact combined
Jacobian: the `a` column comes from the fixed-`c` second-variational system and
the `c` column from the fixed-`a` system. Each direction requests 100 steps at
2.5 times its source secant length.

All points must retain the real `-1` event, orbit closure, eigenvector
normalization, arclength condition, and exact historical/Barrio phase counts
6/8. The combined range must reach at least `c<=6.25` and `c>=8.25` without
large parameter jumps. The two terminal points must independently recorrect
under Radau.

Manifest:
[`../../experiments/manifests/EXP-212-period6-flip-pseudoarclength-extension.json`](../../experiments/manifests/EXP-212-period6-flip-pseudoarclength-extension.json).

## Claim boundary

A pass establishes a broad regular sampled flip-curve segment. It does not
find the physical endpoints, qualify period-12 children over the extension,
identify the TBA, prove global connectivity, or establish double-critical
membership.

## Result

The symmetric claim fails. The upper direction completes all 100 requested
points and reaches `c=8.40309`; the lower direction accepts 23 points through
`c=6.941289` before the next point fails historical phase identity. All 123
retained points preserve exact 6/8 historical/Barrio counts, with maximum
orbit residual `8.25e-13`, event-eigenvector residual `2.00e-12`, and
arclength residual `2.75e-15`. Both retained terminal events independently
recorrect under Radau.

A deterministic replay of the rejected point at
`(a,c)=(0.2158711064,6.9324593154)` retains an accurate real `-1` event and
eight Barrio phases but has seven historical phases. Thus the stop nominates
a historical-section grazing, not a physical termination of the flow-orbit
flip curve. EXP-213 prospectively freezes its direct refinement.

Raw receipt: `artifacts/EXP-212/receipt.json`, 162,359 bytes, SHA-256
`a322c78612874a3735a169e647c66aaa4fdddf81397d39d691ecc6c6e7ec04f1`.
Compact receipt:
[`receipts/EXP-212.json`](receipts/EXP-212.json).
