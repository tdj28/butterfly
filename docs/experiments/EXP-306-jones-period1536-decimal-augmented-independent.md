# EXP-306 — Independent augmented audit of the eighth-event candidate

Status: completed — passed all ten gates

EXP-305 establishes a fourth-order-converged classical-RK4 orbit-plus-
antiperiodic-tangent root but rejects EXP-302's inherited micro-bracket. The
rejected interval came from only approximately corrected long-orbit rows and
is not reused as a physical bound.

EXP-306 independently solves the same augmented equations with the
algebraically distinct RK4 3/8 tableau at 1,024, 2,048, and 4,096 steps per
each of 2,048 segments. The target-blind parameter bound is the full successful
EXP-300 continuation envelope, fixed before this run as
`[0.24070100816116163, 0.24070100823781396]`.

All residual, fourth-order convergence, cross-tableau coordinate/period,
node, tangent-line, and primitive-separation gates are frozen from the
validated independent seventh-event design. A pass qualifies a primitive
eighth numerical real-`-1` event from two independent tableau sequences. It
does not qualify a period-3072 child, the eighth birth's direction, or a
universality limit.

Manifest:
[`../../experiments/manifests/EXP-306-jones-period1536-decimal-augmented-independent.json`](../../experiments/manifests/EXP-306-jones-period1536-decimal-augmented-independent.json).

## Result

All three independent RK4 3/8 augmented profiles converge. The 4,096-step
orbit/tangent residuals are `5.05e-28/7.72e-25`, and primitive half-node RMS
remains `7.99e-6`. Parameter and period convergence ratios are
`15.7210/15.7069`.

The independent Richardson coordinate is
`a=0.24070100822411182396537557542452`. It lies inside the target-blind
successful continuation envelope and differs from EXP-305's classical-RK4
Richardson coordinate by only `2.05e-14`. Extrapolated periods differ by
`7.21e-11`; finest nodes agree within `1.24e-10` maximum and `5.04e-11` RMS;
base tangents agree within `5.73e-13`; and every pointwise tangent-line cosine
passes, with global cosine differing from one by only `4.51e-23`.

The two-tableau consensus midpoint is
`a=0.24070100822410155263404953635485`, with cross-tableau spread
`2.05e-14`. EXP-306 therefore qualifies the eighth primitive numerical
real-`-1` event while preserving EXP-302's rejected micro-bracket. The sixth
finite spacing ratio is `5.312`; the expanded sequence remains non-monotone
and is not a universality estimate. Period-3072 existence and the eighth
birth's criticality remain open.

Raw receipt: `artifacts/EXP-306/receipt.json`, 703,299 bytes, SHA-256
`28972c4727ea48191311f8684be79a183782578d6463989cf3b3cca06f21f843`.
Compact receipt:
[`receipts/EXP-306.json`](receipts/EXP-306.json).
