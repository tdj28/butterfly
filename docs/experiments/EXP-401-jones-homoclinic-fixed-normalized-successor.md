# EXP-401 — Fixed-normalized homoclinic successor

Status: frozen; not yet executed

EXP-400 holds `Delta c=3.125e-8` fixed, but the local tangent's scaled `c`
component falls by `4.27x` at EXP-399.  The normalized step consequently rises
from the passed `0.00459868` to `0.0196159`, and the corrector finds an interior
backward root.  Direction is its sole failed gate.

EXP-401 freezes normalized arclength `0.0045986807364392585` directly.  The
runner orients the recomputed EXP-399 tangent toward positive `c` and derives
the physical `c` request from that local tangent.  The exact EXP-396/EXP-399
sources, canonical unit-weight plane, wall-free bounds, final forward gate,
512 arcs, analytic sensitivities, CSR/LSMR corrector, 40-evaluation budget,
manifold/Radau settings, and every root, arclength, conditioning, tangent, and
margin threshold remain unchanged.

A pass adds a thirteenth qualified above-section curve point and establishes
the first adaptive normalized-step successor.  Neither outcome alone qualifies
the historical intersection, uniqueness, proof, or global topology.

Manifest:
[`../../experiments/manifests/EXP-401-jones-homoclinic-fixed-normalized-successor.json`](../../experiments/manifests/EXP-401-jones-homoclinic-fixed-normalized-successor.json).
