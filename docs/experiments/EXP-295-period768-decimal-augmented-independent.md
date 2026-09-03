# EXP-295 — Independent augmented audit of the seventh-event candidate

Status: completed — passed all ten gates

EXP-294 establishes fourth-order convergence of the classical-RK4 augmented
coordinate but preserves disagreement with the old Float64 tangent field.
EXP-295 tests the newly converged object rather than relaxing that historical
source gate. It independently corrects the full orbit-plus-antiperiodic-tangent
system with the algebraically distinct RK4 3/8 tableau at 1,024, 2,048, and
4,096 steps on every segment.

The independent `a` and period sequences must each converge with a ratio in
`[12,20]`; finest and extrapolated coordinates must remain inside the untouched
EXP-280 bracket and agree with EXP-294 within `1e-10`. The finest orbit nodes,
normalized base tangent, and globally sign-aligned tangent-line field have
separate prospective identity gates. All residual and primitive half-orbit
gates remain unchanged.

A pass independently qualifies a resolution-converged primitive seventh
real-`-1` event representation and may supersede FND-101's event retraction.
It cannot establish the criticality or stability of the period-1536 birth.

Manifest:
[`../../experiments/manifests/EXP-295-period768-decimal-augmented-independent.json`](../../experiments/manifests/EXP-295-period768-decimal-augmented-independent.json).

## Result

All three RK4 3/8 augmented systems converge. Final orbit/tangent residuals at
4,096 steps are `5.18e-28/7.84e-27`, and half-orbit RMS remains `2.58e-5`.
The independent `a` and period convergence ratios are `15.7210/15.7069`.
The independent Richardson coordinate is
`0.24070100823760069070`, inside the original bracket.

Agreement with the classical sequence is much tighter than every frozen gate:
the Richardson coordinates differ by `2.05e-14`, extrapolated periods by
`3.60e-11`, finest nodes by `1.24e-10` maximum and `5.04e-11` RMS, and base
tangents by `1.61e-13`. The global tangent-line cosine is
`0.99999999999999999999995`; every pointwise direction passes the `0.999`
threshold. This independently supersedes the old Float64 tangent field rather
than relaxing its failed identity gate.

EXP-295 qualifies the seventh primitive real-`-1` event. The midpoint of the
two Richardson coordinates is `a=0.24070100823759041937`; the cross-tableau
spread is `2.05e-14`. With that coordinate, the fifth finite event-spacing
ratio is `4.244`, replacing the spurious `2.239` derived from the frozen
Float64 representation. FND-102 records the promoted scope. Criticality and
stable period-1536 attraction remain open.

Raw receipt: `artifacts/EXP-295/receipt.json`, 359,466 bytes, SHA-256
`447f5b7b73206f985b21b0848f2804117aef5c47602df82a6dd7bbf947a39c77`.
Compact receipt:
[`receipts/EXP-295.json`](receipts/EXP-295.json).
