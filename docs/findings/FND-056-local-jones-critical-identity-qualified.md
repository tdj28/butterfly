# FND-056 — The local Jones critical identity is qualified through the support gap

Status: supported under the declared historical-section operational definition

EXP-183 passes factor-two RK4 step-size parity, two independent attractor
references, 128/128 attractor capture at both steps, all local x/z variants,
and five-return DOP853 audits at the sole `a=0.156` hole. Its physical critical
locations agree between steps to `0.000586` in x and `2.24e-7` in z and land
on the predictions frozen from neighboring EXP-180 rows.

Together with EXP-177--180, this qualifies a local operational identity across
the attracting/survivor path: the one critical point of the two-branch
partition continues to the higher-coordinate critical point of the
three-branch partition. The result is representation-bounded and finite-data;
it does not resolve the global shallow-critical birth, continue a TBA curve,
or determine Jones's historical alphabet.

That last boundary applied at this checkpoint; the separately frozen
source-geometric EXP-185 test later qualifies the operational alphabet in
FND-057 without changing EXP-183's claim.

Evidence: [`../experiments/EXP-183-jones-gap-sprinkler-parity.md`](../experiments/EXP-183-jones-gap-sprinkler-parity.md).
