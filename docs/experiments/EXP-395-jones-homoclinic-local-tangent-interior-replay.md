# EXP-395 — Interior-bound local-tangent replay

Status: executed; failed prospectively after finding an interior root

EXP-394's quarter step terminates normally with `7.14831e-9` maximum block
defect and passing tangent/conditioning gates, but its predictor was only
`1.225e-7` from the forward optimizer wall.  It was therefore incompatible
with the unchanged `1e-6` global-interiority gate before the solve began.

EXP-395 removes only that optimizer wall.  It retains the independent final
`c>current` direction gate, `Delta c=1.25e-7` (`0.02254` normalized step), the
wide angle interval, 512 arcs, analytic sensitivities, weighted metric,
CSR/LSMR corrector, 40-evaluation budget, manifold/Radau settings, and every
tangent, root, arclength, conditioning, and scientific margin threshold.  The
runner now preflights the predictor against the frozen acceptance margin.

A pass adds a twelfth qualified above-section curve point.  A backward result
or non-root remains a preserved failure; neither outcome alone qualifies the
historical intersection, uniqueness, proof, or global topology.

## Result

EXP-395 finds an interior, root-nominated boundary-value solution but fails the
two remaining prospective gates:

```text
(a, c) = (0.1798175207507825, 10.31708141841324)
Delta c from current = -7.032864424161289e-8
maximum block defect = 2.338614271646346e-9
arclength residual = 6.99334253700945e-14
minimum singular value = 4.958157520047647e-10
```

The optimizer converges by gradient tolerance after 32 evaluations, all node
and global margins pass, and the root and local-tangent gates pass.  However,
the result is backward in `c`, and the smallest singular value is `0.84%`
below the prospective `5e-10` floor.  Its departure angle moves by `0.47244`
radians while normalized node motion remains `0.04081`.

This preserves a high-quality nearby boundary-value root but does not add a
twelfth forward curve point.  The large angle change nominates the weighted
closing-plane metric as the next controlled variable.  EXP-396 therefore
tests the mathematically standard local-tangent normal at zero step before any
further forward continuation.

Raw receipt: `artifacts/EXP-395/receipt.json`, 85,364 bytes,
SHA-256 `d6dbf80cd17f0e3c4df7d531433c904091a53b6b9023e32b4e947ae10d2924c9`.
Compact receipt: [`receipts/EXP-395.json`](receipts/EXP-395.json).

Manifest:
[`../../experiments/manifests/EXP-395-jones-homoclinic-local-tangent-interior-replay.json`](../../experiments/manifests/EXP-395-jones-homoclinic-local-tangent-interior-replay.json).
