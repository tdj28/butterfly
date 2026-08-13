# FND-071 — The lower-c critical has a qualified finite-data scale

Status: prospectively qualified finite-data scale result; invariant topology
and double superstability remain open

EXP-201 replaces EXP-200's binary smoothing veto with seven logarithmically
spaced smoothing levels. It audits the complete 104-point disagreement set at
both RK4 `dt=0.01` and `dt=0.005`, using nested 2,048- and 8,192-trajectory
supports extracted from the same integrations.

The frozen experiment passes: 94 candidates qualify against a minimum of 70.
Every candidate passes both return-pair gates. Among the 94 qualified points,
86 have identical transition indices in all four step/support reconstructions;
the remaining eight differ by one ladder step, within the frozen maximum of
two. Their normalized second-critical location span has median `0.01031` and
maximum `0.01679`, safely below the `0.03` gate.

Across the resulting 376 qualified support-profile reconstructions, 344 retain
three branches through smoothing `4.6416e-5` and first return two at `1e-4`.
Twenty-five retain three through `2.1544e-5`, are unresolved at `4.6416e-5`,
and return two at `1e-4`; seven transition between `2.1544e-5` and
`4.6416e-5`. The ten failed candidates fail only because at least one of their
four reconstructions lacks a monotone resolved three-to-two transition.

This result upgrades the shallow critical from an arbitrary high-smoothing
disagreement to a reproducible finite-data scale object. It supports reopening
the Jones/Barrio critical-membership residual with a scale-aware estimator. It
does not determine whether two or three branches survive the infinite-data,
zero-smoothing limit, prove a global topology-changing curve, or identify a
doubly superstable shrimp center.

Evidence: [`../experiments/EXP-201-jones-critical-smoothing-scale-audit.md`](../experiments/EXP-201-jones-critical-smoothing-scale-audit.md).
