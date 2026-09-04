# Public core-data replay

The first core bundle supplies a small, explicit set of inputs that can be
checked on an ordinary CPU. It includes one archived parameter-plane panel,
a period-6 flip candidate, and the initial 32-segment homoclinic candidate.
Its scope is narrower than reproducing the entire research campaign.

The frozen allowlist is [`experiments/core-bundle.json`](../experiments/core-bundle.json).
The seven data/protocol files occupy **4,991,221 bytes**, before compression:

| Included input | Bytes | Replay purpose |
| --- | ---: | --- |
| EXP-021 `frame-005.json` | 4,961,884 | Redraw the 26,931-point, `b=0.2` recurrence atlas |
| EXP-021 `frame-005.receipt.json` | 862 | Verify the frame, historical source commit, and manifest hash |
| EXP-205 `receipt.json` | 6,080 | Reevaluate the `flip-c7192` corrected orbit and multiplier |
| EXP-342 `receipt.json` | 16,175 | Reevaluate the preserved 32-arc homoclinic candidate |
| Original EXP-021 manifest | 777 | Preserve the atlas integration/classification protocol |
| Original EXP-205 manifest | 2,106 | Preserve the flip solver and acceptance gates |
| Original EXP-342 manifest | 3,337 | Preserve the local manifold construction and solver gates |

The archive also contains `LICENSE`, `pyproject.toml`, `uv.lock`, the frozen
allowlist, and `index.json`. The index records every file's size and SHA-256,
the exporting source commit/tree, whether its working tree was dirty, and the
locked environment hashes. Historical source revisions remain in the
unchanged experiment receipts. The included generated research data use the
repository's GNU GPL version 2 license. Copyrighted reference PDFs, local
credentials, SSH material, machine logs, and unrelated research outputs are
outside the allowlist.

## Replay a release

Use the source revision named by the release, obtain its core `.tar.gz`
asset and published SHA-256, then run from that checkout:

```sh
uv sync --locked --extra dev
uv run --no-sync python scripts/replay_research_bundle.py \
  --archive /path/to/butterfly-core-v1.tar.gz \
  --sha256 RELEASE_ARCHIVE_SHA256 \
  --output-dir artifacts/core-replay
```

Replace the archive path and checksum with the release's actual values.
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
python3 scripts/verify_research_bundle.py /path/to/butterfly-core-v1.tar.gz \
  --sha256 RELEASE_ARCHIVE_SHA256 --extract artifacts/core-inputs
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
  --output artifacts/releases/butterfly-core-v1.tar.gz
```

It prints the compressed size, archive SHA-256, and full index for review.
The tar and gzip timestamps/ownership are fixed, so exporting the same
revision and input bytes produces the same archive. Existing archives are
refused. `--allow-dirty` exists solely for local draft review and explicitly
records `dirty: true`; a release should be exported from the reviewed clean
commit. Exporting does not upload or publish anything.
