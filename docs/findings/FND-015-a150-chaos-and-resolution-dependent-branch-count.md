# FND-015 — The `a=0.150` set is chaotic and its old two-branch label is resolution-dependent

Status: strong diagnostic result from a prospectively failed full gate

## Result

EXP-118 tests the apparent near-neighbor reversal between the qualified
three-branch saddle at `a=0.149` and EXP-109's nominal two-branch aperiodic
candidate at `a=0.150`. The full experiment fails, but the failure removes the
basis for calling the latter robustly two-branch.

All eight 1200-return datasets remain nonperiodic: four burn-ins from 1000
through 10000 time units and four independent Sobol section seeds after the
longest burn-in. Both Lyapunov cases have a positive largest exponent and a
flow-compatible near-zero middle exponent. The variational largest exponents
are `0.06762` and `0.06204`; independent two-trajectory estimates are `0.05974`
and `0.07068`, differing by at most `0.00865` under the frozen `0.03` gate.
Both uncertainty-aware classifications are chaotic.

The two Lyapunov rows miss only the separately frozen `1e-6` trace-identity
gate: their errors are `2.80e-6` and `2.74e-6`, comparable to earlier DOP853
control-scale errors. This preserves the full experiment's failure while
providing strong evidence that the sampled set is persistent chaos rather than
a short periodic-capture transient.

## The branch-count diagnosis

The strict oracle requires all 15 bin/smoothing variants to agree, so no
dataset receives a final label. The disagreement is highly structured:

- among 48 coarse 20-bin cells, 46 return two and two are unresolved;
- among 192 cells with 30, 40, 60, or 80 bins, 189 return three and three are
  unresolved;
- no coarse cell returns three and no 30--80-bin cell returns two;
- the same split recurs across both coordinates, all four burn-ins, and all
  four basin probes.

Thus EXP-109's 40-bin two label is not reproduced when its global
three-percent prominence cutoff is replaced by the already qualified local
uncertainty rule. At adequate bin resolution the shallow additional extremum
is repeatedly visible. A new resolution-convergence experiment must be frozen
before calling `a=0.150` three-branch, but the alleged `0.149/0.150` topology
reversal is no longer supported.

## Implications

This is favorable to the local Jones/Barrio branch-addition substrate: the
apparent immediate reclosure of the third branch was a classifier artifact,
not a qualified dynamical contradiction. It also demonstrates why a single
global prominence threshold cannot locate a branch-opening curve; topology
and resolution must be converged together.

The next gate treats the 20-bin result as an explicit under-resolution control,
requires new independent 30--80-bin datasets to converge on three branches,
and repeats the trace audit at tighter solver tolerance. Until that passes,
`a=0.150` is qualified as neither two- nor three-branch under the full oracle.

EXP-119 now passes that successor. Five new, doubled-length datasets reproduce
all 30 coarse two-branch controls and all 120 adequate-resolution three-branch
cells; tighter Lyapunov calculations also close the trace gate. FND-016 records
the qualified result. EXP-118 remains a failed but correctly diagnostic
predecessor.

Raw receipt SHA-256:
`fec3f8d9c06b4cf670938f9d17ea97c18a2a4a0e23ec9af80fe43b597da2e9bc`.
