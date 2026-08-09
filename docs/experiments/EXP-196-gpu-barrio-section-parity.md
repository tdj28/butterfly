# EXP-196 — GPU Barrio-section parity

Status: executed; passed exactly at both RK4 steps

## Question

Does the generalized Float64 CUDA survivor kernel reproduce the CPU reference
on Barrio's positive-x section when the full eight-phase second-landmark cycle
is used?

## Frozen computation

EXP-196 is self-contained in tracked source. At the exact source coordinate
`(a,b,c)=(0.215,0.2,7.6)`, DOP853 independently recovers the historical
period-6 attractor, shoots the flow orbit, and extracts all eight crossings on
Barrio's `x=x_-`, positive-`dx/dt` section. The same 2,048 initial states on the
historical half-plane feed CPU and GPU survivor reconstructions at RK4 steps
`0.01` and `0.005`.

Both backends use capture coordinates `(y,z)`, scales `(15,0.01)`, five
consecutive near-cycle returns, a 200-unit horizon, and the same 80--140
midpoint window. The scalar return map is explicitly `z_n -> z_(n+1)`. At
each step both CPU and GPU must resolve a robust three-branch map under all five
oracle variants, retain at least 500 final survivors and 4,000 return pairs,
agree in survivor fractions within `0.03`, and agree in normalized critical
midpoints within `0.03`. Neither backend may suffer a numerical failure.

Manifest:
[`../../experiments/manifests/EXP-196-gpu-barrio-section-parity.json`](../../experiments/manifests/EXP-196-gpu-barrio-section-parity.json).

## Claim boundary

Passing qualifies this new section mode for a separately frozen multi-
candidate GPU discovery scan. It does not establish critical membership,
select a center, or validate the full component.

## Result

The secure RTX A5000 execution from clean commit `c942b46` passes both
profiles. At `dt=0.01`, CPU and GPU match the complete survivor sequence
`[2023,1956,1852,1740]` and all 16,405 return pairs. At `dt=0.005`, they match
`[2023,1957,1855,1739]` and all 16,376 pairs. Both independently resolve three
branches under all five oracle variants.

The maximum normalized CPU/GPU critical-midpoint differences are
`1.57e-11` and `8.24e-11`, far below the frozen `0.03` ceiling. Neither backend
has a numerical failure. The two physical critical intervals remain stable
under step refinement near `z=0.02359--0.02363` and
`z=0.02569--0.02577`. The generalized Barrio-section CUDA path is qualified
for the separately frozen multi-candidate scan.

Compact receipt: [`receipts/EXP-196.json`](receipts/EXP-196.json).
