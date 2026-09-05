# EXP-476 - Homoclinic radius-by-tolerance grid

Status: implementation and analytic-control qualification; target not yet run.

## Question and frozen design

EXP-475's tolerance refinement shifted `a` more than its last radius change.
This study applies three tolerances (`1e-6`, `1e-7`, `1e-8`) at each of three
equal departure/arrival radii (`0.01`, `0.005`, `0.0025`). It tests whether
discretization effects can be separated from finite-endpoint effects at the
initial `(b,c)=(0.2,10.3084)` candidate. It does not test the later turn.

The [v2 manifest](../../experiments/manifests/EXP-476-homoclinic-radius-tolerance-grid.json)
binds the unchanged EXP-342 trajectory by SHA-256. Every case independently
reconstructs its initial guess from that trajectory; cases are not warm-started
from earlier grid solutions. The model, endpoint equations, parameter/time
box, and short DOP853 replay settings remain those of EXP-475. The replay
defect must now be no larger than the individual collocation tolerance.

For each radius, `D1=|a(1e-7)-a(1e-6)|` and
`D2=|a(1e-8)-a(1e-7)|`. Discretization qualifies only if
`D2<=1e-9` and `D2<=0.3*D1+1e-10` at every radius.

Adjacent radii are compared at the common finest tolerance. Classification
order is fixed before target execution:

1. **Below declared empirical resolution:** both the radius difference and
   neighboring summed `D2` are at most `1e-9`.
2. **Resolved:** otherwise, summed `D2` is at most one-quarter of the radius
   difference.
3. **Unresolved:** neither preceding test passes.
4. **Unavailable:** required numerical cases failed or are missing.

The overall `passed` field requires all nine technical cases and all three
discretization comparisons. Endpoint-effect classification is reported
separately. These empirical thresholds are not rigorous error bounds.

## Implementation and safeguards

- The existing v1 four-case manifest remains supported; EXP-475's frozen
  manifest and raw receipt are unchanged.
- v2 validates a complete Cartesian grid and metadata-keyed comparisons,
  avoiding positional assumptions in the original four-case analysis.
- A target invocation requires clean source and exact agreement between the
  selected manifest bytes and its tracked HEAD version.
- Each case has a cooperative 45-second deadline spanning seed construction,
  collocation and replay. Controls and all cases share a 300-second total
  deadline. The node cap is 48,000. A long native solver operation cannot be
  forcibly preempted by callback checks; over-budget results are not accepted.
- The analytic Duffing controls use tolerance `1e-8`. Positive `mu` is an
  energy-injecting negative control, since `H'=mu*y^2`. Its rejection must be
  a completed numerical result, not a timeout or node-budget failure.
- Collocation paths are checkpointed before replay. Failed numerical gates,
  source reads, timeouts, and expected numerical exceptions retain failed and
  skipped cases. Nonfinite diagnostics cannot pass and are preserved as
  explicitly identified `null` entries in valid JSON.
- Technical failures stop later cases. A sensitivity comparison failure does
  not erase accepted solutions or trigger a retuned run.

The controls-only development invocation passed, without reading or solving
the Rössler target. A source commit and tag must be recorded before the target
command below is executed. Its output path must be new.
The complete pre-run suite passes 655 tests. The intended protocol tag is
`exp-476-protocol`; preserve that source even if the implementation PR is
later squash-merged.

```sh
uv run --locked python scripts/validate_projected_homoclinic.py \
  --manifest experiments/manifests/EXP-476-homoclinic-radius-tolerance-grid.json \
  --output artifacts/EXP-476/receipt.json
```

## Interpretation limits

Finite-radius sensitivity is not existence in the infinite-time limit,
uniqueness, a rigorous parameter interval, or validation of Jones's printed
coordinate. Reusing the same source trajectory and finding nearby parameters
does not prove trajectory identity. Selected pre-turn/turn points require a
separate prospective protocol and explicit identity checks after this study.
