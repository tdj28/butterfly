# EXP-110 — Reference sprinkler qualification on the published saddle controls

Status: executed; failed as preregistered

The attracting-set bracket in EXP-109 cannot reproduce the PRL's central
advance inside stable windows. Implement a CPU reference sprinkler sampler
before scaling the ensemble on Runpod. The method follows the survival-ensemble
logic of Kantz--Grassberger and retains the middle-time states of trajectories
that have not yet captured; PIM/stagger-and-step methods remain independent
alternatives rather than retrospective rescue.

At the exact Barrio section, independently recover the stable period-4 orbit at
both published regular controls, `a=0.118` and `a=0.149`. Seed a frozen
`128 x 64` grid on the section over `y in [-38,-8]` and
`z in [0.0088,0.0102]`. Integrate Float64 RK4 at `dt=0.01` to time 300. Declare
capture only after eight consecutive section returns within scaled distance
`0.002` of the stable four-cycle, using scales `(30,0.0006)` in `(y,z)`.

Retain the section crossings during times `[120,180]` only for trajectories
that survive to 300. Form return pairs within each survivor trajectory, never
across trajectories. The primary and cross-coordinate branch oracles must
recover the PRL saddle claims: two branches at `a=0.118`, three at `a=0.149`.

Pass each control only if:

- DOP853 independently recovers the coexisting stable period-4 cycle;
- the survivor count decays but leaves at least 20 of 8192 trajectories;
- neither numerical escape nor nonfinite failure occurs;
- both `y` and `z` provide at least 200 within-trajectory return pairs and the
  expected resolved branch count; and
- a deterministic audit of up to eight survivors and eight captured seeds
  agrees with DOP853 capture classification at least 90 percent of the time.

This is a deliberately difficult qualification. Failure freezes the first
numerical obstruction and triggers grid/horizon/capture-definition diagnosis;
it may not be turned into a saddle claim by plotting the longest transient.
A pass qualifies the CPU reference only. A Runpod/Triton implementation must
then reproduce survivor identities, survival curves, and return-map topology
before a plane-scale saddle scan.

## Result

The experiment ran from clean source commit `b9d5354` in 31.79 seconds and
failed its frozen gate. Both DOP853 references are stable period-4 cycles and
neither 8192-member ensemble has a numerical failure. At `a=0.118`, 2775 final
survivors supply 23,022 return pairs in each coordinate, and both coordinates
resolve the expected two branches at bootstrap consensus `1.0`. At `a=0.149`,
1564 survivors supply 12,892 pairs, but the frozen 3-percent prominence rule
returns two rather than three branches in both coordinates. The pointwise
fixed-step/DOP853 capture audits agree on only 12/16 and 13/16 labels.

The negative result is retained. A post-result diagnostic shows a shallow
additional maximum at `a=0.149`; lowering prominence to `0.005` for `y` and
`0.010` for `z` recovers two critical points with 100/100 bootstrap agreement.
This diagnostic does not change the failed status. See FND-007 for the
scientific interpretation and the statistical-convergence replacement.
