# EXP-175 — Split-cloud Jones-section operational partition

Status: executed; strict experiment failed on held-out `z` bootstrap consensus

## Question

Can a fresh dense return cloud at the established `(a,b,c)=(0.2,0.2,20)`
three-branch control support a neutral operational partition on the recovered
Jones section, independently in `x` and `z`, without using any Figure 6 target
cycle or historical symbol label?

## Frozen design

The run at source commit
`aefee0f35676f6131234ff81de3431ad03514e70` used the negative-oriented
historical half-plane, DOP853, a 1200-time-unit transient, and a 9000-time-unit
observation. The return sequence was split by index into 550 calibration
pairs, a 100-pair guard gap, and 550 held-out validation pairs. Seven frozen
bin/smoothing/prominence variants, each with 100 bootstrap resamples, had to
resolve three branches in both coordinates. Operational labels were fixed as
`B0/B1/B2` and `K0/K1`; no Jones-alphabet mapping was permitted.

Manifest:
[`../../experiments/manifests/EXP-175-jones-section-operational-partition.json`](../../experiments/manifests/EXP-175-jones-section-operational-partition.json).

## Result

The integration succeeded with 1370 accepted crossings. Calibration passed in
both coordinates, and held-out `x` passed all seven variants. Its joint
calibration/validation partition is

- domain `[-30.829893326951613,-8.560969592967794]`;
- `K0` interval `[-25.576689389180185,-25.416041204283548]`;
- `K1` interval `[-17.414284216320493,-16.97460458769476]`;
- maximum normalized joint critical span `0.0197441`, below the frozen `0.04`
  gate.

Held-out `z` failed the unanimity gate. Six of seven variants resolved three
branches. The 50-bin variant retained two nominal critical points, coverage
`0.72`, and conditional spread `0.01236`, but its bootstrap consensus was only
`0.64`, below the frozen `0.8` threshold. There was no contradictory resolved
branch count. The strict robust consensus was therefore `6/7`, and the full
experiment failed as designed.

## Interpretation

This is a power-limited near-pass, not a qualified two-coordinate partition.
It strengthens the evidence that `x` supports the declared three-branch
operational partition and shows that the corresponding `z` geometry is
nominally present, but DEC-014 requires the cross-check to pass rather than be
explained away. A successor must increase independent sample support without
relaxing the oracle thresholds or censoring the failed 50-bin variant.

Raw receipt SHA-256:
`18014be724884e1c9335ff28c4e8f433918b1839a4f8edb5c33f98fc3669621c`.
Compact receipt:
[`receipts/EXP-175.json`](receipts/EXP-175.json).
