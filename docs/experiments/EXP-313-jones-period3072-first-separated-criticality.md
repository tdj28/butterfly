# EXP-313 — Criticality at the first separated period-3072 prefix row

Status: completed — failed because parent and child are both unstable

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

## Result

DOP853 and Radau independently correct the same parent and child and pass every
nonclassification gate. Parent moduli are `1.0023029158/1.0023672000`, clearly
beyond the unchanged `1e-4` neutral margin. Child moduli are
`22667.8828618/22667.8901561`, also strongly unstable. Relative parent/child
spreads are only `6.41e-5/3.22e-7`; parent solver-node RMS is `7.91e-10` and
the child nodes are identical because both solvers accept the exact source row.
All matching residuals remain below `9.61e-9`, half-period nonclosures are
`1.2536e-4/1.2513e-4`, and exact `3584/4096` identities pass.

The frozen result fails only because both families are unstable, giving
`other-or-unresolved` rather than a stability exchange. Combined with
EXP-310's strongly unstable near-event child and neutral parent, and the
EXP-311/312 parameter reversal, this shows that continuation farther along
the daughter branch crosses to the parent-unstable side and does not by itself
resolve local birth direction.

The secure ledger remains eight exact events and six independently qualified
supercritical births through a stable primitive period-768 child. Period 3072
exists and is strongly unstable, but eighth-birth criticality remains open.
The next protocol must localize the parent real-`-1` event separately under
DOP853 and Radau, then switch or sample the child on the common coexistence
side. Another blind farther continuation is not justified.

Raw receipt: `artifacts/EXP-313/receipt.json`, 765,961 bytes, SHA-256
`31713599cd595f690cec64a3a5a32f72a1e326fa0cde52e78adebc24fa1ae39a`.
Compact receipt: [`receipts/EXP-313.json`](receipts/EXP-313.json).
