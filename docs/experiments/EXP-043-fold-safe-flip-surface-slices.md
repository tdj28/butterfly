# EXP-043 — Fold-safe multi-c flip-surface slices

Status: executed; failed formal gate with four-of-five geometric reversals
Manifest: `experiments/manifests/EXP-043-fold-safe-flip-surface-slices.json`
Claim target: persistence of the EXP-035 projection fold under changes in `c`

## Hypothesis and method

The minimum-`b` reversal found on the fixed-`c=5.1` flip curve is not an
isolated slice accident. It persists across the local EXP-038 surface patch and
therefore forms a fold line on the three-parameter flip surface.

At each frozen value `c in {4.9,5.0,5.1,5.2,5.3}`, take the accepted EXP-038
events at `a=0.24125` and `a=0.24` as the oriented seed pair. Continue the full
double-covered flip event system for 60 pseudo-arclength predictors toward
lower `a`. This representation is retained because it is the already qualified
event system; EXP-041/042 establish its fundamental flip meaning.

## Acceptance and limits

Each slice must produce at least 30 corrected points, reach `a<=0.225`, and
keep closure, eigencondition, flow-orthogonality, and arclength residuals below
`1e-8`. At least four of five slices must show a reversal in the `b` projection.

Passing supports a local fold line on the flip surface and supplies a
fold-safe strip suitable for atlas overlays. It does not prove global surface
connectivity, establish a cusp, or show that the surface bounds every shrimp.
Failure will be retained as either evidence against fold persistence or a
resolution/guard limitation, according to the recorded diagnostics.

## Result

The clean run at commit `6f731f32c9658d8b31d9782400097eac2c6421aa`
corrected all 60 requested points on every slice. Residuals were uniformly
excellent: maximum closure `3.80e-12`, maximum eigen residual `8.01e-13`, and
maximum arclength residual `3.46e-15`.

The overall preregistered gate failed. Four slices (`c=4.9` through `5.2`)
showed a reversal in `b`, meeting the fold-persistence count. The `c=4.9`
slice failed its separate `a<=0.225` reach gate: it attained minimum
`a=0.226896` and then reversed in `a`, so more continuation in the same
direction cannot satisfy that gate. The `c=5.3` slice reached `a=0.208442` and
`b=0.152922` but had not yet reversed in `b` within 60 points.

| `c` | Points | Minimum `a` | Minimum `b` | `a` reversals | `b` reversals | Slice gate |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `4.9` | 60 | `0.226896` | `0.264624` | 1 | 1 | failed reach gate |
| `5.0` | 60 | `0.220460` | `0.232444` | 1 | 1 | passed |
| `5.1` | 60 | `0.214572` | `0.203152` | 0 | 1 | passed |
| `5.2` | 60 | `0.210600` | `0.176641` | 0 | 1 | passed |
| `5.3` | 60 | `0.208442` | `0.152922` | 0 | 0 | passed slice gates, no reversal yet |

The complete receipt SHA-256 is
`f0ed9a040a89a97bcc07a8d47673c39e775afa9ac3f3f78e31f36cb106c3de6d`.

## Decision

Retain EXP-043 as formally failed. Scientifically, it supplies strong but
incomplete evidence for a fold line: four independent slices reverse in `b`,
and the failure at `c=4.9` is caused by genuine curve geometry rather than a
solver or resolution failure. Freeze a successor that extends only the
unresolved `c=5.3` boundary slice from the last two accepted points. Do not
retroactively relax the EXP-043 minimum-`a` gate.
