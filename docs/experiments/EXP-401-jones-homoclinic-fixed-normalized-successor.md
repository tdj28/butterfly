# EXP-401 — Fixed-normalized homoclinic successor

Status: executed; failed prospectively on direction alone

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

## Result

EXP-401 converges in two evaluations to an interior, conditioned root but does
not pass:

```text
(a, c) = (0.17981749543013872, 10.317081506433865)
Delta c from current = -1.1039169578452857e-9
derived predictor Delta c = +7.326143293420726e-9
maximum block defect = 4.0082901361779e-9
arclength residual = 5.045795014572939e-14
minimum singular value = 1.6809782219646553e-9
```

Direction is the sole failed check.  This is substantially sharper than
EXP-400: holding normalized arclength fixed prevents its `4.27x` step
inflation, the corrector closes in two evaluations, and the final reversal is
only `1.10e-9` in `c`.  The result therefore isolates finite-step curvature
across a very small local positive-`c` turning radius; it is not evidence that
the homoclinic root disappears or becomes ill-conditioned.

EXP-402 quarters the normalized step to `0.0011496701841098146`, preserves
every other scientific setting and gate, and derives its physical `c`
predictor from the same local tangent.  A quadratic curvature estimate from
EXP-401 predicts that this smaller correction should remain forward.

Raw receipt: `artifacts/EXP-401/receipt.json`, 78,801 bytes,
SHA-256 `ae24d6954296c0b357a1731da3f03b921a42d35f074cf022e1ce593f53ef9386`.
Compact receipt: [`receipts/EXP-401.json`](receipts/EXP-401.json).

Manifest:
[`../../experiments/manifests/EXP-401-jones-homoclinic-fixed-normalized-successor.json`](../../experiments/manifests/EXP-401-jones-homoclinic-fixed-normalized-successor.json).
