# FND-105 — The seventh returning-arm birth is locally supercritical

Status: qualified by the combined EXP-318--320 evidence

At `a=0.24070100823781396`, EXP-299 historically classified a nominal
primitive period-1536 candidate as stable, while EXP-318 resolves its
period-768 parent as stable with an `824.1` multiplier signal/error ratio. The
resulting apparent stable/stable pair could not itself determine the seventh
flip's criticality; EXP-324 later shows that the nominal child does not survive
exact correction.

EXP-319 and EXP-320 remove the mixed-representation ambiguity by switching the
passed period-768 event and doubled daughter using the same 50-digit RK4 3/8
map at 4,096 and 8,192 steps per segment. At each resolution, both tangent
signs and two amplitudes converge. All immediate daughters are primitive and
stable, with moduli `0.92877`--`0.98228`, and they open toward lower `a` while
EXP-318 places the stable parent side toward higher `a`.

Mean event-relative displacement grows from `1.29205e-13` to `5.17089e-13`
as half-node RMS doubles from `7.88364e-7` to `1.57674e-6`. The independently
repeated parameter-amplitude exponents are
`2.000728180629/2.000728180631`. Resolution-doubling changes event-relative
displacement by at most `9.08e-10` relatively, amplitude by `9.27e-13`, and
child modulus by `1.41e-10`.

This qualifies the immediate seventh daughter on the unstable-parent side and
therefore the seventh local birth as supercritical. EXP-324 then corrects the
stored higher-`a` EXP-299 seed below `1e-20`; its half-node RMS collapses from
`6.31e-6` to `7.38e-20`. In the 4,096-step exact map it is the doubled
period-768 parent, not a primitive daughter or a distinct sheet. EXP-325 is
frozen to repeat that correction at 8,192 steps.

The finding does not establish a global period-1536 basin, a limiting scaling
constant, paired shrimp boundaries, TBA membership, double-criticality, a
homoclinic connection, or global parameter-plane topology.

Tracked receipts: [`../experiments/receipts/EXP-318.json`](../experiments/receipts/EXP-318.json),
[`../experiments/receipts/EXP-319.json`](../experiments/receipts/EXP-319.json),
and [`../experiments/receipts/EXP-320.json`](../experiments/receipts/EXP-320.json).
The target-collapse nomination is tracked separately in
[`FND-106-exp299-child-collapses-to-parent.md`](FND-106-exp299-child-collapses-to-parent.md).
