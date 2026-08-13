# EXP-220 — Exact-event multiscale returning-arm child test

Status: complete — failed three-slice gate; near slice passes locally

EXP-219 serializes a complete negative single-shooting switch: neither signed
direction produces a candidate at any of three events. The two remote source
events also have under-resolved doubled-period singularities under the
inherited integration configuration.

EXP-220 first recorrects each real-`-1` event with the analytic augmented
second-variational system at tighter tolerance. It then probes both signed
secondary nullspace directions at the declared predictor lengths `0.002`,
`0.001`, `0.0005`, and `0.00025`, retaining no failed solve. Every generated
candidate is subjected to the unchanged primitivity, `7/8` versus `14/16`
section identity, period-ratio, parent/child Floquet stability-exchange, and
DOP853/Radau whole-orbit gates.

The directional prediction remains frozen: each event must yield a primitive
stable period-12 child toward lower `a`. A pass is compatible with the
returning arm being an opposing shrimp boundary. A failure may still diagnose
single-shooting conditioning and cannot establish child nonexistence.

Manifest:
[`../../experiments/manifests/EXP-220-returning-period12-children-multiscale.json`](../../experiments/manifests/EXP-220-returning-period12-children-multiscale.json).

## Result

All three exact real-`-1` parent events recorrect and pass. The frozen
three-slice child claim nevertheless fails.

At the near held-out slice `c=7.16299104`, six lower-`a` candidates are
generated. Four candidates from predictor scales `0.0005` and `0.00025`
independently pass every gate. Their period ratios are
`2.0000183--2.0001104`, stable child multipliers `0.15646--0.81849`, unstable
parent multipliers `1.04486--1.27026`, and minimum proper-subperiod closures
`0.04490--0.11355`. Historical/Barrio identities are exactly `7/8` for the
parent and `14/16` for the child. Maximum DOP853/Radau whole-orbit RMS over the
passing children is `2.24e-9`. The two coarser lower-`a` candidates are
primitive and cross-solver coherent but unstable, with child moduli `1.2043`
and `5.8030`.

At `c=7.70247507`, only the smallest scale produces one higher-`a` candidate;
it violates the frozen direction and fails independent periodic correction.
At `c=8.20198618`, no scale produces a candidate. The refined smallest
doubled-period singular values are `4.68e-9`, `1.91e-7`, and `1.78e-6`, so the
last slice remains under-resolved by the frozen single-shooting representation.

The result qualifies local supercritical stability exchange on the returning
arm at one untouched slice, compatible with an opposing shrimp boundary. It
does not extend that interpretation to the middle or far arm, where the child
prediction remains unevaluated. EXP-221 therefore freezes identity-safe
continuation of one qualified near-slice child toward the middle slice.

Raw receipt: `artifacts/EXP-220/receipt.json`, 53,510 bytes, SHA-256
`077f88fd064b0825ed385fa9277f1552b44291e319a42abbc0f218dac142134a`.
Compact receipt:
[`receipts/EXP-220.json`](receipts/EXP-220.json).
