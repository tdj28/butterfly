# EXP-315 — Refine both solver-specific event-eight brackets

Status: passed

EXP-314 passes signed DOP853 and Radau real-`-1` brackets of width about
`5.98e-13`. EXP-315 binds that exact receipt and applies two deterministic
bisection evaluations to each bracket. Every midpoint is a fresh fixed-a
2,048-segment parent correction under the corresponding unchanged solver.

Both final brackets must retain opposite signed dominant real multipliers and
have width at most `1.6e-13`. Matching, phase, direct closure, neutral mode,
and block-Floquet gates remain unchanged.

A pass supplies sufficiently narrow solver-specific event bounds to quantify
their separation and design a representation-aware period-3072 switch. It
does not establish a common event or eighth-birth direction.

## Result

EXP-315 passes after 3,573.27 seconds. DOP853 retains a signed real-`-1`
bracket

`[0.24070100822429846, 0.24070100822444732]`

of width `1.48853e-13`. Radau independently retains

`[0.24070100822399930, 0.24070100822414890]`

of width `1.49575e-13`. All four new midpoint corrections pass matching,
phase, direct closure, neutral-mode, and block-Floquet gates.

The brackets are disjoint: the DOP853 lower bound exceeds the Radau upper
bound by `1.49575e-13`. Their midpoint estimates differ by about `2.988e-13`.
This is a bounded numerical representation discrepancy at the event scale,
not evidence for physical multistability or two distinct bifurcations.

The result rules out using one shared absolute `a` coordinate to classify the
parent with a `1e-4` stability margin. The next switch must therefore be
event-relative under each solver: construct the period-3072 daughter from
each solver's own corrected parent and compare the same signed offset from
that solver's bracket.

Raw receipt: `artifacts/EXP-315/receipt.json`, 514,764 bytes, SHA-256
`0e95f1a653269c443a175f41f9c5d4ede6fbca23f74266da1362e50c0eedd526`.
Compact receipt: [`receipts/EXP-315.json`](receipts/EXP-315.json).

Manifest:
[`../../experiments/manifests/EXP-315-jones-period1536-solver-event-refinement.json`](../../experiments/manifests/EXP-315-jones-period1536-solver-event-refinement.json).
