# FND-102 — Augmented high-precision solves qualify the seventh event

Status: qualified numerical event; birth criticality remains open

The returning-arm period-768 branch has a seventh primitive real-`-1` event
near `a=0.24070100823759` at fixed
`(b,c)=(0.2,7.625815600403827)`. Unlike the retracted frozen-node promotion in
FND-100, this claim corrects the orbit, antiperiodic tangent, period, and `a`
together in 50-decimal-digit arithmetic.

Classical RK4 augmented solves at 1,024, 2,048, and 4,096 steps per each of
1,024 segments give `a` and period convergence ratios `15.718/15.706`. The
finest coordinate is `0.24070100821945929997` and the order-four Richardson
coordinate is `0.24070100823758014804`. Independent RK4 3/8 solves give ratios
`15.721/15.707`, finest coordinate `0.24070100822162978683`, and Richardson
coordinate `0.24070100823760069070`.

The two extrapolated coordinates differ by `2.05e-14` and both lie inside the
untouched EXP-280 bracket. Their finest orbit nodes agree within `1.24e-10`
maximum and `5.04e-11` RMS; base tangents agree within `1.61e-13`; the global
tangent-line cosine differs from one by only `4.51e-23`; and every one of
1,024 pointwise tangent directions passes the prospective cosine gate. Finest
orbit/tangent residuals are below `7.84e-27`, and half-orbit node RMS remains
`2.58e-5`, excluding the period-384 double cover.

The consensus midpoint is `a=0.24070100823759041937`, with cross-tableau
spread `2.05e-14`. It yields a fifth finite spacing ratio `4.244`, so the
qualified sequence is `4.557/4.697/4.300/4.836/4.244`. This finite sequence is
still non-monotone and does not establish a limiting constant or universality.

The qualified scope is seven exact numerical flip events on one returning-arm
orbit, six independently supercritical births, and a stable primitive
period-768 child. EXP-288--291 do not qualify the seventh birth's criticality
or stable period-1536 attraction. Nothing here establishes an eighth event,
paired shrimp boundaries, TBA membership, double-criticality, a homoclinic
endpoint, or global parameter-plane topology.

Evidence:
[`../experiments/EXP-294-period768-decimal-augmented-refinement.md`](../experiments/EXP-294-period768-decimal-augmented-refinement.md)
and
[`../experiments/EXP-295-period768-decimal-augmented-independent.md`](../experiments/EXP-295-period768-decimal-augmented-independent.md).
