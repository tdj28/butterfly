# EXP-315 — Refine both solver-specific event-eight brackets

Status: frozen; not yet executed

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

Manifest:
[`../../experiments/manifests/EXP-315-jones-period1536-solver-event-refinement.json`](../../experiments/manifests/EXP-315-jones-period1536-solver-event-refinement.json).
