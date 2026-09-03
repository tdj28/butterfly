# EXP-173 passes: fixed Jones path qualified through period 16

Date: 2026-08-07

The fixed `(a,b)=(0.1798,0.2)` sequence now contains four complete cascade
rungs. Exact `c` events occur at `3.1807265333384103`,
`4.3100451384813105`, `4.636447200967924`, and `4.7090113823613065`.
Independent Radau child qualifications pass at periods 2, 4, 8, and 16.

For the newest rung at `c=4.716`, the period-8 parent multiplier is
`-1.2072088976` and the period-16 child multiplier is `0.1483901906`. Both
switch arms are the same orbit up to phase, their period ratio is
`1.9999995871`, winding is sixteen, and perturbed recovery agrees to
phase-aligned RMS `7.07e-10`.

The finite event-spacing ratios are `3.45990` and `4.49812`. They support a
converging cascade but are not a universality proof. They also do not close the
symbolic-ordering claim: the later source audit finds no printed exact
historical path equations or reproducible return-map partition, and algorithmic
permutation/kneading comparisons remain required.

The local EXP-173 run took `1107.9` seconds, dominated by serial long-horizon
Radau recovery. The next engineering gate is segmented switching plus
checkpointed, batched recovery with CPU/GPU parity, not an unchanged serial
period-32 extension.
