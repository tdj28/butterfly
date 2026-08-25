# EXP-362 — Third homoclinic pseudo-arclength step

Status: frozen; not yet run

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
