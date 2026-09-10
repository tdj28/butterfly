# EXP-517: test the two new fold leads in both directions

## Prospective execution checkpoint

EXP-516 was normally squash-merged through PR #82 after all four final-head
Python 3.12/3.13 checks passed. Main is
`7116df03db3361afb9f09e1f56395637dd5bf470`; the merge occurred at
2026-09-10T11:53:57Z. Its complete saved-data screen found two
earlier-return cells worth direct testing after retaining all eleven
sign-change nominations and the nine known-grazing classifications.
The [EXP-517 protocol](../experiments/EXP-517-earlier-return-folds.md) now
defines the numerical test; no target result is claimed by this checkpoint.

The four fixed representations are:

| Input history | Initial direction | Fixed u interval |
| --- | --- | --- |
| 4 | 0 | [0.010886807025298047, 0.013386807025298042] |
| 4 | 1 | [0.015396270146115155, 0.018931804052047942] |
| 7 | 0 | [0.013386807025298042, 0.015886807025298044] |
| 7 | 1 | [0.018931804052047942, 0.022467337957980647] |

The second direction's intervals come from matching the first direction's
initial x endpoints on its original affine curve. They are new extensions
of that direction's saved grid, not intervals selected after observing new
trajectories. The z coordinate is not fitted to the reference or a desired
word. Histories four and seven are named explicitly: neither is a pass of
the rejected eighth-return test.

Each candidate gets both solvers, a paired midpoint census, the unchanged
bounded Newton corrector and the complete three-offset fold qualification.
Every full-state input and output must agree with all four existing
depth-four references. The all-four verdict additionally requires all eight
solver representations to agree within 1e-6. Existing gain, projection,
transversality and curvature thresholds remain unchanged. A successful result
would restore a local calibration reference, not verify Jones's C/D dictionary,
primitive-family membership or a chain arrow.

## Checked before target execution

- Sixteen new analytic tests pass in a fresh isolated copy. They cover the
  complete nomination ledger, mapped inputs, both histories and directions,
  missing/failed solver and reference cases, and continuation after failure.
  Four additional checks now explicitly exercise output ordinals five and
  eight and rejection of an earlier prefix disagreement; all twenty focused
  tests pass in `preflight-tests-02.xml`.
- The actual prepare/validate/startup commands pass in that isolated copy:
  **128 source paths, 21 input bindings, 143 unique deployed files**, with no
  raw archive or new target integration required for startup.
- The retained analytic dense-census and fold control bundles replay through
  the unchanged implementations. Receipt:
  `artifacts/EXP-517/preflight-controls-01.json`, SHA-256
  `364823e4ddb92e98b05d3bea2cd3f184e49b0f0e0c8efd71bb79d056b2d8a6ce`.
  These are audits of existing controls, not new control IVPs.

The first standalone control-audit invocation ran before concurrent plan
preparation had finished and raised `FileNotFoundError` without any IVP or
target marker. After the plan was present and validated, the same read-only
control audit completed. No consumed experiment was reset or retried.

The complete local regression run passes **2,809 tests with one Linux-only
skip** (`preflight-suite-01.xml`). The four additional ordinal-prefix tests
were added after that suite collected its tests and pass in the separate
twenty-test run. The final 143-file isolated deployment is checked again in
`preflight-startup-02.json`; every deployed source/input hash still matches.
Manuscript citations/figures, the symbolic control table and whitespace
checks pass. Freeze/live-push and the exclusive target marker are still
required before new trajectories. The cap is 128 target IVPs, 2 GiB including the summary,
3600 seconds, an 11-GiB initial free-space requirement and an 8-GiB continuing
floor. Raw products stay local. No paid review, GPU job or external upload is
needed. The existing source-derived symbolic diagram remains labeled as
historical, not independently reproduced.
