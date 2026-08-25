# EXP-402 — Quarter-normalized homoclinic successor

Status: frozen; not yet executed

EXP-401 removes the normalized-step inflation exposed by EXP-400, converges in
two evaluations, and passes every root, residual, interiority, tangent, and
conditioning gate.  Its final point nevertheless lies `1.10392e-9` backward
in `c`, so direction alone rejects it.  The derived tangent predictor was
`7.32614e-9` forward in `c`; the clean, small reversal isolates finite-step
curvature across a very small local turning radius.

EXP-402 freezes one-fourth of EXP-401's normalized arclength,
`0.0011496701841098146`.  The runner again orients the recomputed EXP-399
tangent toward positive `c` and derives the physical `c` request only after
that orientation.  The exact EXP-396/EXP-399 sources, canonical unit-weight
plane, wall-free bounds, final forward gate, 512 arcs, analytic sensitivities,
CSR/LSMR corrector, 40-evaluation budget, manifold/Radau settings, and every
root, arclength, conditioning, tangent, and margin threshold remain unchanged.

A pass adds a thirteenth qualified above-section curve point.  Neither outcome
alone qualifies the historical intersection, uniqueness, proof, or global
topology.

Manifest:
[`../../experiments/manifests/EXP-402-jones-homoclinic-quarter-normalized-successor.json`](../../experiments/manifests/EXP-402-jones-homoclinic-quarter-normalized-successor.json).
