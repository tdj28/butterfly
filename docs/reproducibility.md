# Public core-data replay

The first core bundle supplies a small, explicit set of inputs that can be
checked on an ordinary CPU. It includes one archived parameter-plane panel,
a period-6 flip candidate, and the initial 32-segment homoclinic candidate.
It also includes the full EXP-475 projected-boundary pilot evidence for inspection.
Its scope is narrower than reproducing the entire research campaign.

The frozen allowlist is [`experiments/core-bundle.json`](../experiments/core-bundle.json).
The nine data/protocol files occupy **6,629,037 bytes**, before compression:

| Included input | Bytes | Replay purpose |
| --- | ---: | --- |
| EXP-021 `frame-005.json` | 4,961,884 | Redraw the 26,931-point, `b=0.2` recurrence atlas |
| EXP-021 `frame-005.receipt.json` | 862 | Verify the frame, historical source commit, and manifest hash |
| EXP-205 `receipt.json` | 6,080 | Reevaluate the `flip-c7192` corrected orbit and multiplier |
| EXP-342 `receipt.json` | 16,175 | Reevaluate the preserved 32-arc homoclinic candidate |
| Original EXP-021 manifest | 777 | Preserve the atlas integration/classification protocol |
| Original EXP-205 manifest | 2,106 | Preserve the flip solver and acceptance gates |
| Original EXP-342 manifest | 3,337 | Preserve the local manifold construction and solver gates |
| EXP-475 `receipt.json` | 1,633,857 | Inspect the complete independent-formulation pilot and its controls; not rerun by the core wrapper |
| Frozen EXP-475 manifest | 3,959 | Inspect the pilot's prospective gates and shared-seed limitation |

The archive also contains `LICENSE`, `pyproject.toml`, `uv.lock`, the frozen
allowlist, and `index.json`. The index records every file's size and SHA-256,
the exporting source commit/tree, whether its working tree was dirty, and the
locked environment hashes. Historical source revisions remain in the
unchanged experiment receipts. The included generated research data use the
repository's GNU GPL version 2 license. Copyrighted reference PDFs, local
credentials, SSH material, machine logs, and unrelated research outputs are
outside the allowlist.

## Replay a release

The [public release](https://github.com/tdj28/butterfly/releases/tag/research-core-v1)
is available under tag `research-core-v1`, bound to source
`13d1e1aa3a079704b26b372e110614c774b0793d`. The core archive is 1,156,243 bytes,
with SHA-256
`eb8d8c244bea1ffc2807132f300f0fa819232cb9c70492e48da1ad3ed4ec8cec`.
It was exported clean and replayed from a fresh public GitHub checkout with
locked Python 3.13 dependencies. The release's `verification.json` records
that prepublication check and its numerical results; it is not a proof.
Local draft archives are not the public release.

The subsequent [public-download verification](reviews/receipts/research-core-v1-public-download.json)
checks anonymous HTTPS acquisition of all four assets, their checksums, the
tagged source, and a new replay of the downloaded archive. All core gates pass.
Its diagnostics match the prepublication run; timing-dependent output hashes
are recorded separately rather than required to be identical.

With the GitHub CLI installed, start from this repository and check out the
tagged source. The download includes the core archive, paper PDF, verification receipt, and
`SHA256SUMS` so all published assets can be checked together:

```sh
git fetch origin --tags
git switch --detach research-core-v1
gh release download research-core-v1 --repo tdj28/butterfly \
  --dir artifacts/releases/research-core-v1
(cd artifacts/releases/research-core-v1 && shasum -a 256 -c SHA256SUMS)
```

Use a fresh download directory; existing assets are not overwritten. You can
also obtain the assets through the
[release page](https://github.com/tdj28/butterfly/releases/tag/research-core-v1)
in a browser. The numerical replay itself needs no GitHub or RunPod credentials.

Then install the locked dependencies and use the checksum published for the
archive, without needing to edit it into this document:

```sh
uv sync --locked --extra dev
core_archive_sha256="$(awk '$2 == "butterfly-core-v1.tar.gz" {print $1}' artifacts/releases/research-core-v1/SHA256SUMS)"
uv run --no-sync python scripts/replay_research_bundle.py \
  --archive artifacts/releases/research-core-v1/butterfly-core-v1.tar.gz \
  --sha256 "$core_archive_sha256" \
  --output-dir artifacts/core-replay
```

`artifacts/core-replay` must not already exist. The command verifies the
archive before extraction, rejects links and unsafe paths, checks every
member against its index and frozen input policy, and verifies that the active
checkout has the matching policy and locked environment files. Only the
trusted scripts from the source checkout execute. It does not run code from
the archive or contact RunPod, and it needs no service credentials or GPU.

The output contains the extracted inputs under `data/`, `atlas-b020.png`,
an atlas receipt, fresh numerical outputs under `numerics/`, and
`replay.receipt.json`. A failed numerical acceptance check makes the command
exit unsuccessfully and remains visible in the new numerical receipts.
Historical receipts are never overwritten.

For verification or extraction alone, which needs only Python's standard
library:

```sh
python3 scripts/verify_research_bundle.py \
  artifacts/releases/research-core-v1/butterfly-core-v1.tar.gz \
  --sha256 "$core_archive_sha256" --extract artifacts/core-inputs
```

An already extracted bundle can be replayed with `--bundle-dir
artifacts/core-inputs` instead of `--archive` and `--sha256`. Its full file
inventory and hashes are checked again.

## What this establishes

The atlas is **rendered from archived classifications**. Redrawing it is a
reproducibility check on the public data and figure pipeline; it does not
reintegrate the 26,931 trajectories. Unresolved pixels remain unresolved,
and are not relabeled as chaotic.

The flip and homoclinic checks **perform new numerical integrations** from
the preserved candidates using explicit, recorded settings. This checks
that their local numerical diagnostics reproduce. The flip corrector must also
remain within `1e-6` in its phase-fixed initial state and `1e-8` in relative
period of the released seed; those reproduction gates are in the bundle policy
and do not establish uniqueness. It does not redo candidate
discovery, establish uniqueness, resolve the complete parameter plane, or
provide an independent existence proof. In particular, a homoclinic
candidate with small segmented defects may still have large one-shot
forward-replay error because of unstable error amplification; the historical
direct-replay diagnostic is included without alteration.

The dependency closure is for these core replay operations. The old EXP-205
discovery manifest still names its upstream EXP-203 field, and EXP-342 names
its historical EXP-341 seed. Those discovery steps are not rerun by the core
command. The selected final candidate receipts contain the states, parameters,
times, and nodes needed by this replay. Reproducing the full campaign requires
a larger archived dependency graph, additional validation, and GPU data.

EXP-475 is included as additional inspectable evidence. Its full receipt and
frozen protocol preserve analytic controls, endpoint-radius reductions,
discretization refinement, and short-arc replay diagnostics. The three-example
core command does **not** repeat that pilot's collocation calculations. Its
independent formulation still shares the Rössler model and initial candidate
with the earlier calculation, and does not establish independent discovery,
radius-to-zero existence, a rigorous parameter interval, or uniqueness.

The archive's environment records the source lockfile. Fresh numerical values
and plot bytes may vary with platform, solver libraries, and rendering
versions; acceptance uses numerical gates rather than requiring identical
new output hashes. The input bytes and historical receipts must match exactly.

## Exporting a reviewed release

The exporter accepts only the frozen files, verifies their existing hashes,
and runs the public credential guard. Inventory without writing an archive:

```sh
python3 scripts/export_research_bundle.py
```

From a clean, committed source revision with the required local artifacts:

```sh
python3 scripts/export_research_bundle.py \
  --output artifacts/releases/research-core-v1/butterfly-core-v1.tar.gz
```

It prints the compressed size, archive SHA-256, and full index for review.
The tar and gzip timestamps/ownership are fixed, so exporting the same
revision and input bytes produces the same archive. Existing archives are
refused. `--allow-dirty` exists solely for local draft review and explicitly
records `dirty: true`; a release should be exported from the reviewed clean
commit. Exporting does not upload or publish anything.

## EXP-476: failed grid and post-result diagnostics

The separate [research-exp476 checkpoint](https://github.com/tdj28/butterfly/releases/tag/research-exp476)
publishes the complete failed accuracy study, two algebraic diagnostics, and
the updated 33-figure manuscript. The earlier `research-core-v1` assets are
unchanged. This is inspectable negative evidence, not a successful nine-case
qualification or a full-campaign archive.

The [public-download check](reviews/receipts/research-exp476-public-download.json)
verifies anonymous access and every asset checksum, then reproduces all six
saved-mesh records, both selected arithmetic records, and both controls from
the downloaded data. This is diagnostic replay, not another target solve.

| Asset | Purpose |
| --- | --- |
| `receipt.json` | All controls, six attempted paths, five passes, one failure, three skipped records |
| `mesh-diagnostic.json` | Reconstructed residuals and prospective node-cap accounting from saved meshes |
| `arithmetic-diagnostic.json` | 80-digit fixed-interval reevaluation and known-solution quantization controls |
| `manuscript.pdf` | Current article and supplement; 61 pages, 33 figures |
| `SHA256SUMS` | SHA-256 checksums for the four assets above |

Download into a new directory and verify every asset before inspection:

```sh
exp476_download_dir=$(mktemp -d)
gh release download research-exp476 --repo tdj28/butterfly \
  --dir "$exp476_download_dir"
(cd "$exp476_download_dir" && shasum -a 256 -c SHA256SUMS)
```

The raw receipt must hash to
`c9818275ed3c585934cdeaa85857b04a5e9a6e1a6400f426a5cbf6e06d5b95bc`.
It was produced once on clean source
`af90d04e6b484733bb2535a453157c4830691a34`, preserved by the pushed
`exp-476-protocol` tag. The diagnostic hashes are listed in the
[experiment record](experiments/EXP-476-homoclinic-radius-tolerance-grid.md).

From the source checkout accompanying `research-exp476`, reevaluate the saved
arrays without integrating or solving another orbit:

```sh
uv sync --locked --extra dev
.venv/bin/python scripts/inspect_homoclinic_grid_mesh.py \
  --receipt "$exp476_download_dir/receipt.json" \
  --output "$exp476_download_dir/mesh-recomputed.json"
.venv/bin/python scripts/inspect_homoclinic_interval_arithmetic.py \
  --receipt "$exp476_download_dir/receipt.json" \
  --mesh-diagnostic "$exp476_download_dir/mesh-diagnostic.json" \
  --output "$exp476_download_dir/arithmetic-recomputed.json"
.venv/bin/python scripts/plot_homoclinic_refinement_grid.py
```

Both diagnostics refuse to overwrite output. The arithmetic check intentionally
uses the original hash-bound mesh diagnostic, not a new environment's rewritten
diagnostic. Mesh inspection uses internal SciPy polynomial-evaluation helpers
and records their source hashes; environment metadata can change regenerated
file hashes. Compare the numerical fields and recorded definitions, not only
whole-file equality. The figure uses only the tracked compact summary.

Preparing release checksums and notes is also scripted:

```sh
.venv/bin/python scripts/prepare_exp476_release.py
```

This checks the four explicit local assets, frozen input hashes, failed outcome,
diagnostic links, and common credential patterns. It creates a new local
release directory without overwriting files, copying assets, or publishing
anything. It must not be used to replace the earlier core release.
