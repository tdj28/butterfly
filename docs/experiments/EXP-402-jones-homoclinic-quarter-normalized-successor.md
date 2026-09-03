# EXP-402 — Quarter-normalized homoclinic successor

Status: executed; failed prospectively on the obsolete positive-c gate

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

## Result

EXP-402 converges in two evaluations to another interior, conditioned root but
does not pass its frozen positive-`c` gate:

```text
(a, c) = (0.1798174935368561, 10.317081502559637)
Delta a from current = -3.464635800476401e-10
Delta c from current = -4.978145895506714e-9
maximum block defect = 4.0063666650173605e-9
arclength residual = 5.016656931633136e-14
minimum singular value = 1.6853573828828708e-9
```

Direction is again the sole failed check.  Unlike EXP-401, reducing the step
does not restore positive `c`; the root instead moves slightly downward in
`a`, toward Jones's fixed-`a=0.1798` section.  Thus `c` is not monotone at this
local fold and cannot remain the continuation direction.  This does not erase
EXP-399 or indicate loss of a homoclinic root.

The runner now supports an explicit tangent orientation and independent
coordinate direction gates.  EXP-403 prospectively replays the same normalized
step, orients the local curve toward decreasing `a`, leaves `c` unconstrained,
and requires final `a` to decrease.  Every root-quality and conditioning gate
is unchanged.

Raw receipt: `artifacts/EXP-402/receipt.json`, 78,797 bytes,
SHA-256 `d6c424a0f6420604a48e84d7cbb2bbcd623c674c276f6bbde6bee67315f11233`.
Compact receipt: [`receipts/EXP-402.json`](receipts/EXP-402.json).

Manifest:
[`../../experiments/manifests/EXP-402-jones-homoclinic-quarter-normalized-successor.json`](../../experiments/manifests/EXP-402-jones-homoclinic-quarter-normalized-successor.json).
