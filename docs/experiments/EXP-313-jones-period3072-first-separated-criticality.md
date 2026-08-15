# EXP-313 — Criticality at the first separated period-3072 prefix row

Status: frozen; not yet executed

EXP-312 fails its full continuation gates but preserves an exact accepted
prefix. EXP-313 selects the first prefix row whose absolute distance from the
bound finite 8,192-step event coordinate reaches `4e-12`. This is step 3 at
`a=0.24070100821872153`; every source row through it must retain matching below
`1e-8` and half-node RMS above `5e-6`. The selection uses no multiplier. The
threshold is nearly four times the finite-to-Richardson coordinate shift in
the bound event receipt.

DOP853 and Radau independently correct the 2,048-segment parent and
4,096-segment child at the fixed coordinate. The unchanged `1e-4`
classification margin applies. Both solvers must pass matching, phase, cyclic
node identity, multiplier spread, child half-period nonclosure, and exact
`3584/4096` section identity. A consistent parent/child stability exchange
passes; unresolved, mixed, or same-stability classifications fail.

A pass qualifies the sampled eighth-birth direction. It does not validate
EXP-312 beyond the selected prefix or establish a globally stable or unstable
period-3072 branch.

Manifest:
[`../../experiments/manifests/EXP-313-jones-period3072-first-separated-criticality.json`](../../experiments/manifests/EXP-313-jones-period3072-first-separated-criticality.json).
