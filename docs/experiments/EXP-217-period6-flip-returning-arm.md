# EXP-217 — Broad continuation of the returning period-6 flip arm

Status: complete — passed all frozen gates

EXP-216 qualifies an exact turn in the `c` projection and stops only because
its frozen upper guard is `c=7.0`. EXP-217 expands that guard to `c=8.8` and
continues from the last two accepted events toward `c>=8.25`.

The adaptive policy and every scientific gate are unchanged. At least 20 and
at most 160 points may be accepted. Each must remain an exact real-`-1`
period-6 event with extremum-partitioned historical count seven, Barrio count
eight, and bounded parameter jumps. The terminal point must independently
recorrect under Radau.

Manifest:
[`../../experiments/manifests/EXP-217-period6-flip-returning-arm.json`](../../experiments/manifests/EXP-217-period6-flip-returning-arm.json).

A pass establishes a broad returning event arm. It does not prove global
closure, assign either arm to a shrimp boundary, continue the child sheet,
identify the TBA, or establish double-criticality.

## Result

All 135 accepted events pass, and the terminal point reaches
`(a,c)=(0.2712670323,8.2527330490)`. The returning arm is monotone in `c` over
this sampled range and retains raw/extremum historical and Barrio counts
`7/7/8` at every point. Maximum orbit, event-eigenvector, arclength, and
extremum-section residuals are `1.26e-11`, `2.92e-12`, `8.49e-12`, and
`4.55e-13`. Nine overlong trials violate only the frozen adjacent-parameter
jump gate; each is discarded, halved, and replaced by an accepted event.

The terminal event independently recorrects under Radau. The `a` difference
is `6.90e-13`, relative period difference `4.63e-13`, state difference
`1.91e-11`, and multiplier-modulus difference `1.47e-7`, all inside the frozen
gates. At common `c`, the returning arm lies above the original arm by
`0.00891` in `a` at `c=7.16`, `0.01328` at `c=7.30`, `0.04329` at `c=8.00`,
and `0.05778` at `c=8.25`.

Combined with EXP-212, 215, and 216, this establishes a broad folded sampled
real-`-1` event locus with two separated arms. It does not yet show that both
arms bound the same stable shrimp, carry corresponding period-12 children,
close globally, or intersect the TBA/double-critical set.

Raw receipt: `artifacts/EXP-217/receipt.json`, 387,231 bytes, SHA-256
`b2ae896f075fc14c5cc580dc657611b041e62dce6eaf44a2da9b155ad39f3b65`.
Compact receipt:
[`receipts/EXP-217.json`](receipts/EXP-217.json).
