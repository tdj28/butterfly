# FND-100 — A seventh returning-arm flip event is numerically qualified

Status: retracted as formulated by FND-101; event later requalified by FND-102

Post-qualification correction changed the evidential status. EXP-292 attempts
to correct the period-768 orbit itself in 50-digit arithmetic rather than only
integrating its frozen Float64 nodes. All three corrections leave the frozen
`1e-6` source neighborhood by `7.32e-5` to `9.32e-5` and their tracked `-1`
root collapses toward the lower-period solution. Therefore the independent
multiplier agreement below remains valid for the frozen representation, but it
does not qualify an exact primitive event. FND-101 records the reopened claim.

The former claim placed a seventh period-doubling event at
`a=0.2407010081734325` on the primitive period-768 branch. The original
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
pass. Under that now-retracted interpretation, the seventh coordinate added a
fifth finite spacing ratio, `2.239`, to
the previous `4.557/4.697/4.300/4.836` sequence. The stronger non-monotonicity
is evidence against estimating an accumulation constant from these early
rungs; it does not refute a later asymptotic regime.

This finding formerly qualified seven exact numerical flip events on one
returning-arm orbit. That statement is withdrawn pending an augmented
high-precision orbit-plus-tangent correction. The first six exact events and
their stable children through period 768 remain qualified. Nothing here establishes a
limiting scaling constant, universality, child sheet, paired shrimp boundaries,
TBA membership, double-criticality, or a global parameter-plane topology.

Evidence:
[`../experiments/EXP-286-period768-decimal-richardson-audit.md`](../experiments/EXP-286-period768-decimal-richardson-audit.md)
and
[`../experiments/EXP-287-period768-decimal-independent-richardson.md`](../experiments/EXP-287-period768-decimal-independent-richardson.md).
