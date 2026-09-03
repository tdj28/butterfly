# EXP-363 — Fourth homoclinic pseudo-arclength step

Status: passed

EXP-363 continues the common-gauge, 128-arc branch from exact EXP-361 and
EXP-362 nodes. All mathematical settings, bounds, the 40-evaluation budget,
the requested `Delta c=0.0005`, and both `1e-8` root gates remain unchanged.

Passing supplies another local point toward a bracket of exact `a=0.1798`.
It cannot alone qualify the historical section, uniqueness, or
computer-assisted existence.

Manifest:
[`../../experiments/manifests/EXP-363-jones-homoclinic-pseudoarclength-step4.json`](../../experiments/manifests/EXP-363-jones-homoclinic-pseudoarclength-step4.json).

EXP-363 passes all ten checks at the 40-evaluation cap. It lands at
`(a,c)=(0.1800825699757035,10.316267272411649)` with maximum matching defect
`9.933499263901978e-9`, matching-residual norm `1.826722405338073e-8`, and
arclength residual `-6.1030104581139e-12`. Node margin is `0.92537`.

The step realizes `87.84%` of the requested `Delta c`. Its local slope is
`-0.3255513694`, projecting exact `a=0.1798` at `c=10.3171352460`. Because
the maximum defect consumes `99.33%` of the root gate, the next predictor is
prospectively halved while every acceptance threshold remains fixed.

Raw receipt: `artifacts/EXP-363/receipt.json`, 30,220 bytes, SHA-256
`78b85011bd678454ca9de5e386f50ce864fb8b59588ef85e99439c877cc626e8`.
