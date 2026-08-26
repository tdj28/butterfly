# EXP-407 — Fourfold post-turn homoclinic step

Status: executed; passed all prospective gates

EXP-406 passes the first genuine secant-aligned chain and confirms that the
recomputed tangent and corrected point both move toward larger `a` after the
local minimum.  Its normalized node displacement is only `0.00235144`, leaving
ample room inside the unchanged bounds.

EXP-407 restores the previously exercised fourfold-larger normalized step
`0.0045986807364392585`.  It binds EXP-405/EXP-406, recomputes the tangent at
EXP-406, aligns it with their full-state scaled secant, leaves `a` and `c`
unconstrained, and requires positive signed arclength.  All root, arclength,
conditioning, tangent, margin, integration, and optimizer settings remain
unchanged.

A pass adds a sixteenth qualified point and measures the post-turn trend more
efficiently.  It does not by itself establish global nonintersection,
uniqueness, proof, or global topology.

## Result

EXP-407 passes every gate in two evaluations:

```text
(a, c) = (0.1798175017664706, 10.317081483432371)
Delta a = +7.46365105830371e-9
Delta c = -1.6310378825323824e-8
signed arclength = 0.004598680736501758
maximum block defect = 4.001272509832052e-9
minimum singular value = 1.6727126293145124e-9
```

This adds the sixteenth qualified point and resolves the local `a` minimum on
both sides: the outgoing branch moves increasingly toward larger `a` and
smaller `c`.  Global nonintersection remains open.  EXP-408 freezes another
fourfold arclength increase, to `0.018394722945757034`, with all gates fixed.

Raw receipt: `artifacts/EXP-407/receipt.json`, 79,059 bytes,
SHA-256 `ce49eaaca34a3f83733ee17d512a0d846dc7ab8720ccbcfcc1ce756fedc5ae61`.
Compact receipt: [`receipts/EXP-407.json`](receipts/EXP-407.json).

Manifest:
[`../../experiments/manifests/EXP-407-jones-homoclinic-postturn-fourfold-step.json`](../../experiments/manifests/EXP-407-jones-homoclinic-postturn-fourfold-step.json).
