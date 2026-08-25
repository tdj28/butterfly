# EXP-368 — Homoclinic pseudo-arclength section bracket

Status: frozen; not yet run

EXP-367 passes only `8.47855e-5` above exact `a=0.1798` with 31% matching-gate
headroom. EXP-368 therefore prospectively returns the 256-arc predictor to
`Delta c=0.0005` using exact EXP-366 and EXP-367 roots. All solver, manifold,
gauge, sensitivity, bound, budget, and acceptance settings remain unchanged.

A pass below `a=0.1798` forms a qualified pseudo-arclength bracket with
EXP-367. It does not itself solve the exact section, establish uniqueness, or
supply computer-assisted existence.

Manifest:
[`../../experiments/manifests/EXP-368-jones-homoclinic-pseudoarclength-section-bracket.json`](../../experiments/manifests/EXP-368-jones-homoclinic-pseudoarclength-section-bracket.json).
