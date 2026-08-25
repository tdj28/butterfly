# EXP-362 — Third homoclinic pseudo-arclength step

Status: passed

EXP-362 binds the exact 128-arc EXP-360 and EXP-361 roots and continues toward
the historical `a=0.1798` section. Both source receipts encode the common
eigenspace gauge, removing the legacy-angle reconstruction needed in the
first two-parameter step.

The requested `Delta c=0.0005`, both free parameters, simultaneous analytic
sensitivities, Radau and manifold settings, source-centered bounds,
40-evaluation budget, matching gate, and arclength gate are unchanged. In
particular, EXP-361's cap-terminated pass does not trigger a post-hoc budget or
threshold relaxation.

Passing qualifies one additional local curve point. It cannot by itself
qualify the historical fixed-`a` intersection or establish uniqueness,
computer-assisted existence, or global topology.

Manifest:
[`../../experiments/manifests/EXP-362-jones-homoclinic-pseudoarclength-step3.json`](../../experiments/manifests/EXP-362-jones-homoclinic-pseudoarclength-step3.json).

EXP-362 passes all ten checks with normal `gtol` termination after only five
function evaluations. It lands at
`(a,c)=(0.18022554996795825,10.3158280790748)` with maximum matching defect
`8.484944612257776e-9`, matching-residual norm `1.5521662451615815e-8`, and
arclength residual `-5.241129145266976e-12`. Node margin is `0.93532`.

The corrector realizes `90.37%` of the requested `Delta c`. Its local slope is
`-0.3255489647`, projecting the historical section at `c=10.3171352556`.
This third chained root further supports smooth local continuation; it does
not yet qualify the exact section.

Raw receipt: `artifacts/EXP-362/receipt.json`, 22,651 bytes, SHA-256
`b217c3d72915f926c394039ccd512b672178828114b1f82a51289f62737ffcc1`.
