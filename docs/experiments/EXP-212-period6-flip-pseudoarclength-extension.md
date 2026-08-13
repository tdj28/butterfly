# EXP-212 — Broad pseudo-arclength extension of the period-6 flip curve

Status: prospectively frozen before execution

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
