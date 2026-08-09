# EXP-184 — Source-derived Jones historical alphabet

Status: executed; administrative failure before integration

## Question

Can Jones's historical `C,D,0,1,2` alphabet be assigned to the already
qualified neutral partition using source-defined geometry, without computing
or fitting any Figure 6 target word?

## Frozen derivation

The author TeX defines `C` as the critical retained from the unimodal side and
`D` as the added trimodal critical. EXP-183 therefore fixes `K1 -> C` and
`K0 -> D`. The same prose describes the new branch-3 excursion and says that
its deposited orbit point lies in the innermost region. With `D=K0` below
`C=K1`, the outer interval beyond `D` is `B0 -> 2`; the fresh-data geometric
prediction is that `B2` is the unique physically innermost interval and hence
`B2 -> 0`. The remaining interval is `B1 -> 1`.

The derivation is frozen separately at
[`../../experiments/source-transcriptions/jones2012-alphabet-semantics.json`](../../experiments/source-transcriptions/jones2012-alphabet-semantics.json).
It contains no Figure 6 landmark-orbit result and uses no target word to choose
the mapping.

## Frozen test

Two fresh, independently initialized trajectories use DOP853 and Radau at the
qualified trimodal control `(a,b,c)=(0.2,0.2,20)`. Each supplies disjoint
1000-pair calibration and validation segments. In both `x` and `z`, the exact
EXP-176 domain and critical intervals are immutable.

Every solver/segment/coordinate must retain at least 900 fully resolved pairs
and 100 targets in each branch. `B2` must have the smallest median physical
distance to the small equilibrium, a normalized median gap of at least `0.2`,
and strict maximum/minimum separation from both other branches. At least 75
`B0 -> B2` transitions must occur, while `B0 -> B0` may occupy at most `1%` of
resolved `B0` departures. Simultaneous `x/z` source-and-target branch labels
must agree on at least `90%` of jointly resolved pairs.

Manifest:
[`../../experiments/manifests/EXP-184-jones-historical-alphabet.json`](../../experiments/manifests/EXP-184-jones-historical-alphabet.json).

## Result

Direct execution from clean commit `1d70107` stopped in parent-evidence
validation before constructing a solver or integrating a trajectory. The
validator expected every compact receipt to expose a top-level `passed` field;
EXP-183 correctly stores the same value at `gates.passed`. The exact exception
was `parent evidence did not pass: docs/experiments/receipts/EXP-183.json`.

No scientific row or raw receipt was produced. EXP-185 preserves every
trajectory, partition, mapping, and acceptance gate while adding only explicit
dot-delimited pass-field paths to the parent-evidence records.

## Claim boundary

An eventual pass will qualify this historical mapping operationally on the recovered
Jones section. It will not prove that the scalar partition is a unique
generating partition, establish a template/conjugacy, validate a Figure 6
word, or locate a global TBA curve.
