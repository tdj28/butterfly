# After EXP-519: test the periodic reinjection mechanism directly

## Release checkpoint

EXP-519's complete result, compact receipt, tests, figures and manuscript source
are pushed at `73ff7772aea07847175778ffecc6dccd9bd30135` on
`codex/exp519-fixed-c-fold-response`. [PR85](https://github.com/tdj28/butterfly/pull/85)
is open. Both final-head push and PR workflows are running; all four Python
3.12/3.13 jobs must pass before normal exact-head squash merge.

The earlier work-head Python 3.12 failure was two 240-second isolated-replay
timeouts, not a numerical assertion failure. Its one diagnostic retry was
cancelled when the new head was pushed, so that retry supplies no passing
evidence. Keep the original failure and observe the new complete checks.
The frozen target startup and its successful local execution are unchanged.

## Proposed next scientific question, not a frozen experiment

The next useful question is where the **corrected periodic orbit itself**
could acquire an extra inner return. The successful fold contact does not
identify D, but a periodic reinjection-geometry test need not wait for a claim
that the whole double-critical center or symbolic dictionary has been solved.
Word assignment still requires that separate definition and validation.

At a stationary point of the historical section coordinate,
`dy/dt = x + a*y = 0`. Its signed section displacement `g=y-y*` is a direct
candidate grazing residual: `g=0` also gives `x=x*`. The z coordinate and
full speed distinguish a regular projected-center crossing from approach to
the equilibrium. A complete inventory on the actual primitive cycle is more
direct evidence than reusing a transient-curve boundary measured at different
parameters. No old boundary distance or old joint Jacobian is a new measurement.

The proposed first step is a bounded saved-data analysis using **all five
EXP-519 points, both solvers and both periodic windows**, with no new IVPs.
It should retain every candidate extremum, report full states and signed
section gaps, check repeat/solver correspondence and exclude ambiguous
nearest-object selection. Only a qualified, consistently identified object
could supply a fresh local response for a subsequent parameter continuation.
No favorable subset, unbounded extrapolation or automatic D label is allowed.

## An important completeness issue to resolve before freezing

Source inspection of `python/butterfly/periodic_winding.py::observe` shows
that its section extrema come from ordinary `solve_ivp` event callbacks.
The observer then brackets section crossings between those extrema. Replaying
that observer is not an independent certificate that no extrema were missed.
The EXP-519 numerical qualification and audit remain exactly as stated; do
not silently promote them to a stronger completeness theorem.

Before nominating a closest periodic grazing object, investigate an independent
complete census on each retained DOP853/Radau observation polynomial. Here
`x+a*y` is linear in the state, so its restriction to a stored dense segment
is a polynomial of bounded degree. Use exact coefficient conversion or
controlled interval arithmetic, explicit segment-endpoint ownership, and
analytic missing-root/multiple-root controls. A certificate for those stored
polynomials is still not an exact-flow root-completeness proof. Cross-method
state/phase checks and numerical error qualifications remain necessary.

The complete-polynomial census is a proposed design, not an executed result.
Do not inspect target extremum gaps to tune its thresholds or pick a branch.
Shape/hash-only inventory can size its workload. Preserve every unresolved
root interval and any disagreement with the previously reported extrema.

## Execution-order amendment before target outcomes

The initially proposed sequence below made PR85's merge a prerequisite. Source
inspection establishes that this is unnecessary: EXP-520 imports existing main
numerical helpers, not EXP-519 execution code. Its only new dependency is the
immutable public EXP-519 audit receipt. On 2026-09-10 the next branch was
therefore cut from fresh main (`1895bfd42a8ab54bf88ce47131be4d53a6c041ba`),
and that one receipt was restored byte-for-byte from the published release
commit. Its SHA is unchanged. PR85 remains open and must still pass its own
full CI before merge; no failed test is waived. This ordering change happened
before any new extremum census or gap was computed. It avoids making unrelated
release waiting a scientific gate.

The new post-run CI correction is on PR85 at
`048955c347adec72fb68e3e2396fd221dcbb1b59`. Three completed final-head jobs
failed only an unnecessary exact-equality assertion on norm ratios, differing
by one or two last-place bits. The production verifier passed. A fourth
Python 3.12 job was still running when the correction was pushed. The new
assertion permits at most four ULPs for that norm-derived field only and passed
45 local tests; frozen scientific sources and thresholds are unchanged.

EXP-520's preflight initially exposed a macOS `/var` versus `/private/var`
path comparison error in the new isolated startup test. Resolving the temporary
root, rather than weakening source-origin checks, repaired it. No trajectory
coefficients had been opened. The draft root bracket was tightened from
`1e-11` to `1e-15` before outcomes, to leave adequate room for the already
planned state-box precision during rapid z motion. All 37 initial tests then
passed, including the authentic isolated consumer. The first prepared draft
plan hash was `add8912e4dd1243769b9df97e7f29c8ba53bb694b3deb3806fb112ae67af7282`;
it was not a public source freeze and was not executed.

## Original proposed execution order (superseded as above)

1. Finish PR85's final-head checks; preserve any timeout without editing frozen
   scientific sources or bypassing CI. Merge only on all-green checks.
2. Cut the next work branch from the resulting fresh main. Keep EXP-519's
   source, receipt, attempt marker and local raw evidence immutable.
3. Build and test the smallest complete stored-cycle census and comparison
   protocol, including source/input hashes, output admission and failure records.
4. Freeze and live-push that design before its target analysis. Execute it,
   audit its complete results and use them to decide the next actual periodic
   continuation test. Do not stop at the plan when its gates permit execution.

No paid Pro review, GPU worker, new integration, raw upload or new symbolic
verification has occurred in this successor preparation.
