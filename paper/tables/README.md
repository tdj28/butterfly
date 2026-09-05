# Auditable manuscript tables

- `review001-equilibria.json` records both equilibrium roots and local spectra
  at the printed hub, initial numerical candidate, and two scalar-classifier
  endpoints. It compares the package/NumPy calculation with independent
  80-digit Decimal polynomial algebra, including a same-binary64-Jacobian
  comparison. Source hashes and environment versions are included. It is
  not interval validation, a homoclinic computation, or an exclusion of either
  equilibrium's global role.
- `review001-saddle-bracket.csv` is the four-row PIM endpoint/horizon summary
  shown in the methods supplement. Each row names its tracked source summary;
  regression tests compare the values against those summaries. These are
  robustness variants, not four independent statistical replications. This
  table is not a new PIM run or a full inventory of every classifier point.

From the repository root, reproduce the algebraic check into a new output:

```sh
.venv/bin/python scripts/report_review001_equilibria.py \
  --output artifacts/review001-equilibria-replay.json
.venv/bin/python -m pytest -q tests/test_review001_equilibria.py \
  tests/test_review001_presentation.py
```

The command refuses an existing output path. Results retain declared decimal
inputs and numerical comparison diagnostics; platform/NumPy version changes
need not produce byte-identical new files. The tests enforce numerical checks
and the binding of the committed snapshot to its recorded sources.

These tables improve access to the selected evidence. They do not supply the
full raw arrays behind all manuscript figures; see the paper's Data/code
availability section and `docs/reproducibility.md` for the actual public scope.
