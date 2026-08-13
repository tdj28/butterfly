# FND-100 — A seventh returning-arm flip event is numerically qualified

Status: qualified finite numerical finding

The exact returning-arm continuation contains a seventh period-doubling event
at `a=0.2407010081734325` on the primitive period-768 branch. The original
Float64 DOP853/Radau representation could not pass the unchanged `1e-7`
multiplier gate because its parameter sensitivity exceeds Float64 resolution
(FND-099). That failure is preserved rather than rewritten.

EXP-286 evaluates the immutable orbit and tangent representation with a
50-decimal-digit classical-RK4 sequence at 4,096, 8,192, and 16,384 steps per
segment. EXP-287 repeats all 1,024 segments with the algebraically distinct
fourth-order RK4 3/8 tableau. Both show near-order-four raw convergence and
converged Richardson estimates:

| tableau | extrapolated flip multiplier |
|---|---:|
| classical RK4 | `-0.9999999948282761` |
| RK4 3/8 | `-0.9999999948805051` |

Their difference is `5.22e-11`; the independent value lies `5.12e-9` from
`-1`. All prospective convergence, neutral-mode, cyclic-product,
characteristic-polynomial, orbit, tangent, primitive, and exact-section gates
pass. The seventh coordinate adds a fifth finite spacing ratio, `2.239`, to
the previous `4.557/4.697/4.300/4.836` sequence. The stronger non-monotonicity
is evidence against estimating an accumulation constant from these early
rungs; it does not refute a later asymptotic regime.

This finding qualifies seven exact numerical flip events on one returning-arm
orbit. Only the first six have separately qualified stable children, through
period 768. A period-1536 switch and two-solver stability exchange are required
before calling the seventh birth supercritical. Nothing here establishes a
limiting scaling constant, universality, child sheet, paired shrimp boundaries,
TBA membership, double-criticality, or a global parameter-plane topology.

Evidence:
[`../experiments/EXP-286-period768-decimal-richardson-audit.md`](../experiments/EXP-286-period768-decimal-richardson-audit.md)
and
[`../experiments/EXP-287-period768-decimal-independent-richardson.md`](../experiments/EXP-287-period768-decimal-independent-richardson.md).
