# Reproduce EXP-494 without new integrations

EXP-494 tests projected winding and conditional minimal period on corrected
periodic cycles, then surveys 64 nearby parameter nodes using two solvers.
It does not verify a Jones symbolic word or insertion arrow.

## Results and artifact layers

- **Primary:** 806 integrations, 116 attempted profiles, 54/64 new parameter
  nodes qualified, two rejected as repeated shorter cycles, eight dependent
  nodes not run. Both paired bases qualify. All eight earlier EXP-480
  profiles pass the new minimal-period diagnostic.
- **Post-run diagnostic:** both rejected points give three historical and
  four Barrio returns over half the nominal period, with projected winding
  three. This does not replace the primary failures or locate a flip.
- **Public compact data:** the complete primary summary, compressed without
  changing its bytes; all node/profile/window decisions remain available.
- **Full raw data:** four tar shards containing 1189 files / 2,140,190,117
  member bytes, including all trial meshes, observation polynomials, source
  bindings, required EXP-480 inputs and the EXP-494 attempt marker. This
  closes this replay's dependencies, not the entire earlier research campaign.

The archive release is [research-exp494](https://github.com/tdj28/butterfly/releases/tag/research-exp494).
All eleven assets were published and their server-reported sizes and SHA-256
digests matched the local files on 2026-09-09. A fresh public download of the
index and compact data also matched. The full local bundle's fresh-directory
replay passed; the four raw shards were not downloaded a second time for replay.
Its Git tag supplies the release/replay code; the original numerical source is
`4e5054955e8ddeb9db94e4702fe78d6232eda303`, separately preserved at
`codex/exp494-local-execution`. Data retain the repository's GPL-2.0-only license.

## Acquire and replay

From a fresh checkout of the release tag, install the locked development
environment (`uv sync --locked --extra dev`). Download the four tar assets and
the index into one new directory:

```sh
gh release download research-exp494 --repo tdj28/butterfly \
  --pattern 'EXP-494-full-data-*' --dir artifacts/EXP-494/download-v1
```

The index SHA-256 is
`bcc740f263211dd71a8e0f5db9e02f42acaa803aadcf7b5bd9862bb2be450611`.
The extractor checks every archive and member, rejects unsafe paths and
nonregular entries, and requires a **fresh output directory**. It never
overwrites old evidence or reruns the consumed experiment:

```sh
PYTHONPATH=.:python .venv/bin/python -m scripts.release_exp494_periodic_transport \
  --extract-and-replay \
  --index artifacts/EXP-494/download-v1/EXP-494-full-data-index.json \
  --index-sha256 bcc740f263211dd71a8e0f5db9e02f42acaa803aadcf7b5bd9862bb2be450611 \
  --output-dir artifacts/EXP-494/replay-v1
```

Allow approximately 2.15 GB for downloaded shards and another 2.15 GB for
the extracted data. This is a storage description, not a runtime estimate.
The resulting `public-replay.json` checks all primary node decisions and
blocked-arm seed relationships. Replayed events come from stored solver
polynomials, not new numerical integration. The
[I/O adapter amendment](experiments/EXP-494-audit-io-amendment.md) explains why
the unchanged frozen audit is called through a cached-array loader.

For the **outcome-informed secondary diagnostic**, run separately:

```sh
PYTHONPATH=.:python .venv/bin/python -m scripts.analyze_exp494_shorter_cycles \
  --run artifacts/EXP-494/replay-v1/artifacts/EXP-494/target-4e50549 \
  --output artifacts/EXP-494/shorter-cycle-replay.json
```

Its two original primary statuses must remain `unqualified`. The archived
secondary output records the source commit used when that analysis was first
run; a later replay records its own checkout commit, so compare the numerical
rows rather than expecting identical provenance bytes.

The figure needs only the compact data already checked into Git:

```sh
MPLCONFIGDIR=artifacts/EXP-494/mpl-config PYTHONPATH=.:python .venv/bin/python \
  -m scripts.plot_exp494_periodic_transport \
  --source docs/experiments/receipts/EXP-494-periodic-transport-data.json.gz \
  --sha256 ac783c3183ff028b0c0289cd7740d441b4ac76b11655fade0ae010836488bf9f \
  --output-dir artifacts/EXP-494/figure-replay
```

Numerical floating-point replay allows narrowly bounded arithmetic roundoff;
identities, integer counts and Boolean decisions are exact. Byte-identical
figure output also depends on the plotting/font environment. Figure receipts
bind source, generator, all plotted rows and all outputs; this is not an
independent-team replication or a rigorous all-root/minimal-period proof.

## Checksums and availability

| Shard | Bytes | SHA-256 |
| --- | ---: | --- |
| `EXP-494-full-data-00.tar` | 536791040 | `e70e6e22ebd3484eb391ff865385bfa2be8987a2a3dfafa6b8cc1ed079c0dd86` |
| `EXP-494-full-data-01.tar` | 533678080 | `8dfc17bb8a586ea30943a846877822c40804309d1be3af9d9720036e522567a2` |
| `EXP-494-full-data-02.tar` | 534927360 | `cb9eb5f0786418bae40cffa465ff7e000121baabff5635777e47cb3e8f40448e` |
| `EXP-494-full-data-03.tar` | 535726080 | `3435d8fc04b69d512ca9cb08bf786f5bf89d7e24b5b5686bd300423847945aa0` |

The compact data and the complete index are under
`docs/experiments/receipts/`. The raw shards are release assets, not Git
blobs. Local full extraction/replay passed before publication; the
[dated update](updates/2026-09-09-exp494-periodic-winding-transport.md)
records the separate live release verification and its limits.
