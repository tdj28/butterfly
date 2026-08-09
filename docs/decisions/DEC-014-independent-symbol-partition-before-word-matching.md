# DEC-014 — Infer the symbol partition before matching Jones words

Date: 2026-08-07

Status: adopted; operational encoder and synthetic assignment controls
implemented; end-to-end dynamic qualification pending

## Context

The Figure 6 source audit produces a precise finite target, but the paper does
not print the Poincaré-section equation, invariant domain, scalar coordinate,
partition thresholds, or uncertainty rule used to turn an orbit into a word.
A stable period-`p` orbit supplies only `p` return points. Fitting critical
points to those same points and then declaring their word a match would be
circular.

The original referee also distinguished the abstract branched manifold from a
coordinate-dependent phase-space picture. The machine test must preserve that
distinction: a scalar word can be qualified without being promoted to a
template invariant.

## Decision

Symbolic reproduction will have three immutable layers.

### 1. Source target

The hash-bound Figure 6 transcription fixes the 23 words, ten doubly-supported
`p -> p+1` arrows, one visual-only arrow, three lower-period relationships, and
ten approximate parameter landmarks before any modern orbit is labeled. A
source correction requires a new transcription version and visual evidence.

### 2. Independently inferred return partition

The primary historical representation is the recovered section through the
small equilibrium's `y` coordinate, with `x<x_eq`; this gate implies negative
orientation. The primary scalar coordinate is `x`, with `z` as a mandatory
cross-check, matching the qualified scope of EXP-107.

Critical intervals must be inferred from a dense transient or invariant-saddle
return cloud, never from the target stable cycle alone. DEC-004's coverage,
graph-likeness, prominence, and bootstrap gates remain binding. Section
offsets, coordinate changes, bin count, smoothing, sample density, and
conditioning horizon are frozen before the target orbit is corrected.

Ordered scalar intervals receive an operational branch code fixed by section
orientation and increasing primary coordinate. The historical numerals `0`,
`1`, and `2` are attached only after a source- or topology-supported mapping is
declared in advance. `C` and `D` are assigned only when a periodic point
intersects the corresponding independently estimated critical interval and a
local zero-slope residual passes. A visually convenient relabeling after seeing
the Jones word is forbidden.

### 3. Independently corrected orbit and word

The periodic orbit is recovered with flow shooting, primitive-period checks,
whole-orbit phase identity, Floquet stability, and DOP853/Radau parity. Its
states are withheld from partition fitting. The resulting cyclic word is
canonicalized under cyclic rotation only; reversal or alphabet permutation is
reported as a separate comparison, not silently accepted.

## Acceptance sequence

1. Synthetic one-, two-, and three-branch controls must recover their frozen
   partitions and words.
2. Published two- and three-branch Rössler controls must pass the dense-cloud
   partition gates on the declared representation.
3. The ten approximate Figure 6 landmarks are classified without expected
   labels. An unresolved or different period is retained and does not by
   itself reject the figure because the coordinates are explicitly approximate.
4. Any local landmark refinement radius, mesh, objective, and budget are
   preregistered before searching.
5. Every Figure 6 word and arrow is tested. The visual-only arrow remains a
   weaker gate and may not be pooled with the ten doubly-supported arrows.
6. A held-out word or arrow is predicted before its target orbit is computed.

## Consequences

- The qualified period-16 cascade remains dynamical evidence, not symbolic
  evidence.
- A match in `x` that fails the `z` cross-check is representation-dependent and
  cannot close RVR-004.
- Failure to map the operational interval code uniquely onto Jones's numerals
  is an explicit unresolved source-convention result.
- Template or conjugacy language remains unavailable without the stronger
  invariant-set and bijection tests in RVR-001 and RVR-004.
- The next experiment may classify the ten printed parameter landmarks, but it
  may not tune a partition or local search to make their labels agree.

## Implementation checkpoint

`python/butterfly/symbolic.py` now implements the non-circular assignment
layer. It requires a finite frozen domain, ordered nonoverlapping critical
intervals, explicit increasing-coordinate branch symbols, and section
orientation provenance. A point inside a critical interval remains unresolved
unless its independently supplied local slope residual clears the frozen
zero-slope threshold. Out-of-domain values are never extrapolated. Cyclic
rotation is canonicalized; reversal is returned only as a separate diagnostic;
and mapping operational symbols onto the historical alphabet must be complete
and explicit.

Thirteen synthetic assignment and grammar tests pass for one-, two-, and
three-branch partitions. These tests qualify the encoder mechanics, not yet
the end-to-end recovery of a partition from a dense Rössler return cloud.
