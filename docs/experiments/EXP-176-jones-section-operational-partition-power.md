# EXP-176 — Powered split-cloud Jones-section operational partition

Status: executed; passed

## Question

Does the one failed held-out `z` bootstrap variant in EXP-175 disappear under a
fresh trajectory with greater independent sample support, while every oracle
and acceptance threshold remains unchanged?

## Frozen design

EXP-176 was committed and pushed before execution. It changed the initial
condition from `[0,4,0]` to `[1,1,1]`, increased the observation horizon to
16000 time units, and froze 1000 calibration pairs, a 200-pair guard gap, and
1000 held-out validation pairs. The seven bin/smoothing/prominence variants,
100 bootstrap resamples, `0.8` bootstrap gate, graph-likeness and coverage
gates, critical-drift bounds, section, solver, and neutral symbols were
unchanged from EXP-175.

Manifest:
[`../../experiments/manifests/EXP-176-jones-section-operational-partition-power.json`](../../experiments/manifests/EXP-176-jones-section-operational-partition-power.json).

## Result

The run at clean source commit
`566674773eeba14e95464a0173298d2438b793f5` succeeded with 2431 accepted
crossings. All seven variants resolved three branches in both segments and
both coordinates; every variant consensus is `1.0`.

The joint neutral partitions are:

| coordinate | domain | `K0` interval | `K1` interval | maximum normalized joint span |
|---|---|---|---|---:|
| `x` | `[-30.8298935246,-8.5609724063]` | `[-25.5846726575,-25.4304846162]` | `[-17.4242694773,-17.0310342440]` | `0.0176585` |
| `z` | `[0.00393560515,0.00700509895]` | `[0.00438716153,0.00439620559]` | `[0.00532725733,0.00537696154]` | `0.0161930` |

Both maximum spans are below the unchanged `0.04` joint gate. The output
continues to label increasing-coordinate branches `B0/B1/B2` and critical
intervals `K0/K1`; `historical_mapping` is explicitly `null`.

## Interpretation

The dense three-branch control on the recovered negative-oriented Jones
half-plane now has a calibration/validation-qualified operational partition in
both nondegenerate scalar coordinates. This closes the three-branch control
portion of DEC-014's partition gate and confirms EXP-175's `z` failure was
sample-power-sensitive under unchanged thresholds.

It does not identify `K0/K1` with `C/D`, map `B0/B1/B2` to Jones's numerals,
encode a Figure 6 cycle, validate a transition arrow, or establish a template
invariant. A corresponding historical-section two-branch control and the
independent target-cycle slope/word tests remain open.

Raw receipt SHA-256:
`25c923967c2a2604fb952a40c4ddc410f7c83e2a67e03b61f9a895d4a7c0a889`.
Compact receipt:
[`receipts/EXP-176.json`](receipts/EXP-176.json).
