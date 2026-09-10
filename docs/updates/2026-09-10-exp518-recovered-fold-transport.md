# EXP-518: carry the recovered fold toward the saved primitive cycle

## Parent result is merged and reproducible

EXP-517 recovered the same local fold in all four history/direction
constructions, with both solvers and every full-state reference. All 108
target IVPs passed raw audit. [PR #83](https://github.com/tdj28/butterfly/pull/83)
was normally squash-merged at `2026-09-10T13:04:27Z`, producing main commit
`e1c12894e87f2f38906b4b6d8a53c9b5f57ee786`.
All four push/PR Python 3.12/3.13 checks passed on exact head
`9e253ad9eaae73fe2b79bc1ca7d38bf276571413`; the last finished at
`2026-09-10T13:02:02Z`. Runs: `34477261579` and `34477257299`.
The completed PR Python 3.13 log reports **2,853 passing tests**, with no
research artifacts or credentials available. Its citation, symbolic-control
table and 2,972-file public scan also pass.

The main article now includes the recovered-fold figure and a readable
explanation of its limits. The author remains blank. The old eighth-return
failure remains failed; Jones's flow-level symbolic chains remain unverified.

## Next bounded experiment

A fresh `codex/exp518-recovered-fold-transport` branch starts from that merged
main. The [prospective protocol](../experiments/EXP-518-recovered-fold-transport.md)
keeps all four newly qualified curve constructions and tests the two remaining
fixed EXP-510 parameter substeps, at c approximately 7.157 and 7.152. The
endpoint was already exposed with old constructions in EXP-508/509, so this
is not fully blind parameter validation.

The implementation retains complete midpoint and offset event histories,
both solvers, failed cases, and every raw product. A midpoint outside its
fixed time window is retained as an unqualified seed, not used to enlarge the
window or abort an otherwise affordable complete matrix. All local and
original-region gates remain. The separate transport criteria remain a
1e-6 cross-representation spread and .01 adjacent-state displacement, with
scales `[15,15,.01]`; the latter is not a relaxed accuracy tolerance.

Only a fully qualified two-stage result can compare its endpoint folds with
the saved primitive cycle, at exactly matching parameters. No new periodic
cycle or boundary computation is part of this experiment. Success would
support a new, explicitly bound joint-contact study, not silently reuse the
old depth-eight response model or assign a C/D symbol.

## Preflight evidence, not a target result

- **27 focused tests pass**. They include complete/missing matrices, bad warm
  predecessors, excessive state displacement, time-box exits, conditional
  second-stage execution, complete-prefix disagreement, independent transport
  arithmetic, and mismatched endpoint parameters.
- The **full repository suite plus the draft's 27 tests passes: 2,879 passed,
  one expected Linux-only skip, 636.33 seconds**. It ran from the current
  repository with the draft module namespace; the four code/test files copied
  onto this branch are byte-identical. Receipt:
  `artifacts/EXP-518/draft-suite-01.xml`.
- The actual prepare, validate and copied-source startup commands pass in an
  isolated draft deployment: **135 source paths, 22 input bindings, 151 unique
  files**, without a raw `artifacts` directory or bytecode. Receipt:
  `artifacts/EXP-518/draft-startup-02.json`, SHA-256
  `dde4565b6c14cf21d7f2e964531f9a2c8aae59449bf329dc7ed4766092de8256`.
  Protocol prose was clarified after this check; final-package startup must
  be checked again before the execution freeze.
- Retained analytic dense-census and fold controls replay successfully with
  **zero new control IVPs**. Receipt: `artifacts/EXP-518/draft-controls-01.json`,
  SHA-256 `364823e4ddb92e98b05d3bea2cd3f184e49b0f0e0c8efd71bb79d056b2d8a6ce`.

The final in-repository package check also passes:
`artifacts/EXP-518/preflight-startup-03.json`, SHA-256
`7625f774d5715aaf3818aeb39eb4f27bfe7d07b863edc33cd1ae2c0f7ca9866c`.
All 151 deployed hashes, including the final protocol, match this branch.
The 27 focused tests pass again from their actual repository paths in
`preflight-focused-02.xml`. Frozen plan SHA-256:
`e217455377cbd0b3a8de00ef0455beb2f27c4c92b72dbdc8b4c519591929e058`.
Paper citation/control-table and whitespace checks pass.

No EXP-518 target attempt or numerical result is claimed by this preflight
checkpoint. Exact source freeze and live push remain mandatory before one
exclusive execution. The cap is 256 target IVPs,
3,600 seconds and 2 GiB including summary, with an 11-GiB initial disk
requirement and an 8-GiB continuing floor. No paid Pro request, GPU rental,
remote worker change or raw upload is involved. No numerical evidence was
removed to create disk space.
