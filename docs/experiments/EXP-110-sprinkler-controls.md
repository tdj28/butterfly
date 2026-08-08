# EXP-110 — Reference sprinkler qualification on the published saddle controls

Status: preregistered under DEC-005; not yet executed

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
