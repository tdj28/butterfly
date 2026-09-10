# EXP-518: carry the recovered fold toward the saved primitive cycle

## Audited outcome: transport succeeds; endpoint contact fails

**All 200 target IVPs pass the full local raw audit.** Both new parameter
stages qualify every construction (histories 4 and 7, directions 0 and 1)
with both solvers. The recovered fold can be tracked through the previously
unfinished parameter steps without the collapsed eighth-return construction.
This is finite, local numerical transport evidence, not a rigorous unique
continuation or a verified symbolic chain.

| Stage | Qualified constructions | Full-state spread (limit 1e-6) | Adjacent displacement (limit .01) |
| --- | --- | --- | --- |
| c = 7.157000000000001 | 4/4, both solvers | 1.59942e-13 | .000935145 |
| c = 7.152000000000001 | 4/4, both solvers | 1.85095e-13 | .000936384 |

The endpoint is **not** a qualified fold–cycle contact. All sixteen
construction/solver/repeat-window variants pass the x-only comparison but
fail the full input/output-state comparison at the unchanged 1e-4 threshold:

- worst projected pair distance: **9.05541e-5**;
- worst full-state pair distance: **1.39565e-4**, about **1.396 times** the limit;
- every full-state variant fails, not just one disagreeing solver.

The reused boundary distance remains about .0111383, roughly 111 times
the same threshold; no new boundary was computed. Thus neither a joint
critical contact nor a C/D assignment is established. The x-only pass is
specifically insufficient: the three-dimensional check prevents a false
positive. The old depth-eight failures remain failures.

This is useful progress for reconstructing Jones's proposed mechanism:
we have removed a local transport obstruction and localized the remaining
fold/cycle mismatch. It does not verify or debunk the paper's symbolic
chains. The next calculation must bind the recovered four/seven-return
families and qualify their response before any new correction; it cannot
silently reuse the old depth-eight Jacobian. Separately, the missing second
smooth critical geometry must be established before labeling a doubly
critical itinerary. Reducing a grazing-boundary residual alone cannot do that.

### Exact evidence

- Source: `bc404a33d6270070f3ee91730105d5610e0024a0`, preserved at
  `codex/exp518-local-execution`.
- Plan SHA-256: `e217455377cbd0b3a8de00ef0455beb2f27c4c92b72dbdc8b4c519591929e058`.
- Raw summary SHA-256: `162cf3b2c870cfa6b3db6a34efa66c3af132ed9eaf31cbaad46534e1e95e59e1`.
- Full local raw audit and identical public compact receipt SHA-256:
  `f8a0b33cd13ff88d924928bc5f59a811468ae5a627ca007a0541702d194c8e01`.
- Raw completion: `2026-09-10T14:23:51.452590+00:00`; elapsed
  919.106446 seconds including isolated runtime startup, 288 files and
  733,372,449 bytes including summary, below the frozen 2-GiB cap.
- [Public compact receipt](../experiments/receipts/EXP-518-recovered-fold-transport-result.json):
  2,821,136 bytes. It does not include the complete raw meshes. Those remain
  local; neither remote backup nor independent-team replication is claimed.

The following sections preserve the preflight and execution chronology.

### Release checks and interpretation audit

The public verifier reconstructs midpoint seeds, compact Newton algebra,
all accepted event prefixes, local qualification, both transport decisions,
the exact endpoint comparison and the listed IVP count. It does not claim
to re-integrate the flow or independently audit absent raw meshes, polynomial
census completeness, raw control bundles or disk totals. The full local
raw audit is a separate retained artifact, not a substitute for releasing
the underlying data.

The public consumer and its rehashed semantic-mutation tests pass: **34 tests**,
including an isolated 153-file deployment with no raw `artifacts` directory.
The separate figure controls pass **16 tests**. The full repository suite
passes **2,888 tests with one expected Linux-only skip** in 664.34 seconds.
That suite excluded the not-yet-produced receipt-dependent public tests and
was collected before seven additional endpoint-figure controls; those are
covered by the later focused runs, not silently counted in the earlier suite.

A same-agent adversarial interpretation pass explicitly rejected three
overclaims: eight solver profiles are not independent discoveries; a passing
projection cannot override failed full-state proximity; and continuation of
one fold is not identification of both C and D. The figure displays the
failed endpoint comparisons beside the passing transport comparisons.
This is a local audit, not independent-team verification.

The first PDF rendering prompted larger chart labels and a float barrier so
the new paragraph is not interrupted by older figures. An early draft figure
replay overlapped these formatting edits and is not used as reproducibility
evidence; the final outputs require a fresh, byte-identical regeneration.
No frozen numerical source or raw evidence was changed.

Final release checks are now complete locally:

- **77 focused tests pass** (transport, compact replay, semantic mutations,
  source-only consumer and figure controls), in 303.40 seconds. A final
  published-figure binding test was then added; all **17 figure tests** pass
  in 9.25 seconds. That additional test checks the actual plotted values,
  source/generator/verifier hashes, image formats, receipt index and paper copy.
- All five final figure products regenerate **byte-identically** from the
  audited receipt in fresh directories (`figure-02` and `figure-replay-02`).
  [View the figure](../figures/EXP-518-recovered-fold-transport.png).
- The local manuscript builds cleanly to **75 pages with 38 figures**
  (13 main, 25 supplemental). Its author remains blank. The final changed
  text and figure pages were rendered and visually checked; no LaTeX warnings
  remain. The PDF is local only, not a new public PDF release.
- Citation and symbolic-control-table checks pass. The public staged scan
  checks 2,990 files; the frozen numerical source inventory remains unchanged.

No paid Pro request, GPU rental, remote worker mutation or raw upload was
made. The raw evidence and exclusive attempt marker remain local and intact.
The release branch must pass all final-head push and PR checks before normal
squash merge; local completion does not imply it has already reached main.

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

## Execution started

The exact source `bc404a33d6270070f3ee91730105d5610e0024a0` is now
live-verified on both `codex/exp518-recovered-fold-transport` and the preserved
`codex/exp518-local-execution` reference. The actual execution binding records
`2026-09-10T14:08:32.336351+00:00`; isolated startup and control replay passed,
the exclusive marker was created, and the first numerical stage started.
Raw output is retained locally in `artifacts/EXP-518/target-bc404a3`.
This is execution status, not a completed or audited result. The frozen
source, thresholds, and consumed attempt must not be modified or reset.

The first stage completed with **100 target IVPs and all four constructions
locally qualified**; the frozen controller advanced to the second stage.
These are provisional execution counters, not a substituted raw audit.
The source-freeze push checks also passed (GitHub run `34482744652`).
The 27 transport tests plus nine new synthetic figure tests pass locally;
the release regression suite is running while numerical collection continues.

## Why the geometric test is not yet the symbolic chain

The source was rechecked directly in `references/1201.4343v1.pdf`, especially
pages 3–4 and Figure 6. Jones defines C as the critical point associated with
the two-branch/unimodal side and D as the additional bimodal critical point.
His example follows C100 through C200 to C1000, with the extra inner return
encoded as zero. Thus a successful local fold continuation is a necessary
geometric ingredient for this reconstruction, not a C/D assignment by itself.
The new calculation must not substitute a section-grazing boundary for the
missing second smooth turning point, or infer a chain from a changing return
count alone. A source-matched test still needs the critical geometry,
primitive cycle, operational dictionary and actual window-to-window path.
