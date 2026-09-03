# DEC-015 — Branch distinctness requires exact coordinate matching

Status: adopted after EXP-229

## Problem

EXP-227 compared an exact event curve with linear interpolation of the sparse
EXP-217 receipt. The candidate appeared `5.60e-7--5.85e-7` lower in `a`, more
than ten times its frozen separation gate. EXP-229 corrected the source event
at the identical 21 `c` coordinates and found a maximum `a` difference of
`1.46e-14`. Curvature interpolation error accounted for the whole apparent
gap and produced a false distinct-branch inference.

## Decision

A claim that two orbit-defined event branches are distinct must use at least
one of these comparators at every decisive coordinate:

1. fresh correction of both branches at the same parameter coordinate, with
   orbit, phase, event-vector, multiplier, and independent-solver gates;
2. a validated higher-order interpolant whose numerical error bound is smaller
   than one tenth of the claimed minimum separation; or
3. a two-branch augmented solve that enforces nonzero phase-invariant orbit
   distance directly.

Linear interpolation of stored event coordinates may be used for plotting,
prediction, or seed selection. It may not establish branch identity,
separation, collision, reconnection, or topology.

## Consequence

FND-089 is retracted and FND-088 is corrected. The EXP-223/226 path crossing
is the known returning flip arm, not a second shrimp boundary. Future
continuation scripts must either perform exact same-coordinate correction or
store a certified interpolation-error budget in their receipt.
