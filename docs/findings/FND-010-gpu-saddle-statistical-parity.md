# FND-010 — GPU and CPU recover the same published saddle topology

Status: passed Float64 statistical-parity control

## Result

EXP-113 reproduces the qualified EXP-112 CPU controls on a secure-cloud NVIDIA
RTX A5000. The GPU returns two branches at `a=0.118` and three at `a=0.149` in
both `y` and `z`; all 30 frozen oracle cells have variant consensus `1.0`.
The combined CPU/GPU critical-location spans are at most `0.01463`, below the
preregistered `0.04` gate.

The six checkpoint survivor counts agree exactly for the three-branch control.
For the two-branch control, they agree through the first five checkpoints and
differ by one of 8192 trajectories at the final checkpoint. The maximum
survivor-fraction discrepancy is therefore `1/8192 = 0.0001221`, far below the
frozen `0.02` threshold. No GPU trajectory fails numerically.

Five declared seeds per control also agree with adaptive DOP853 over their
first five section returns: the maximum scaled state error is `2.46e-6` and
the maximum event-time error is `3.16e-6`, against thresholds `1e-3` and
`2e-5`.

## Integrator clarification

The GPU state is advanced in Float64 by fixed-step RK4. Four bounded Newton
updates do not replace RK4: they solve only for the within-step Poincare-event
coordinate on the cubic-Hermite interpolant formed from the RK4 step endpoints
and vector fields. DOP853 supplies a separate adaptive reference for the
short-horizon event audit.

## Provenance and cost

The tracked-source archive binds commit `03a77bf` and has SHA-256
`8d81c77684e420b4e4279fb8966a4ab4781580ed7ecae62af93abc393fd590c5`.
The retrieved 26,569-byte raw receipt has matching remote/local SHA-256
`98428448119c4e428364bfcbcb220b7ae67c81c208abfc409eb44ff1cf5bd48a`.
An adjusted A40 offer at `$0.44/hour` was automatically rejected because it
exceeded the `$0.40/hour` launch cap. The accepted A5000 cost `$0.27/hour`;
total provisioning-to-teardown wall time gives a conservative spend bound
below `$0.06`. Both hosts were terminated and the account list was verified
empty.

## Interpretation

This opens the engineering gate for larger saddle ensembles: GPU acceleration
does not change the qualified local topology observable. It strengthens the
computational reproducibility of the shared Jones/Barrio two-to-three-branch
premise, but it is not an independent dynamical method and does not continue
the TBA. A PIM-triple or stagger-and-step construction remains the next
scientific corroboration gate before saddle-defined continuation through the
regular gap.
