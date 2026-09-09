# Research-update figure receipts

This index starts with EXP-485. It is not a claim that every older figure has
the same per-figure receipt format. Older figure provenance remains in its
experiment documentation and plotting scripts.

| Figure | Audited data | Figure receipt |
| --- | --- | --- |
| [EXP-485 PNG](EXP-485-transported-tangent.png), [SVG](EXP-485-transported-tangent.svg) | [All 80 results](../experiments/receipts/EXP-485-transported-tangent-result.json) | [Inputs, derived values, code/output hashes, alt text](EXP-485-transported-tangent.receipt.json) |
| [EXP-486 PNG](EXP-486-continuous-return-curves.png), [SVG](EXP-486-continuous-return-curves.svg), [PDF](EXP-486-continuous-return-curves.pdf) | [All 16 families](../experiments/receipts/EXP-486-return-image-fold-result.json) | [Complete figure receipt](EXP-486-continuous-return-curves.receipt.json), [hashed index](EXP-486-continuous-return-curves.index.json) |
| [EXP-490 PNG](EXP-490-direct-folds.png), [SVG](EXP-490-direct-folds.svg), [PDF](EXP-490-direct-folds.pdf) | [All 26 candidates and both solvers](../experiments/receipts/EXP-490-direct-fold-result.json) | [Complete figure receipt](EXP-490-direct-folds.receipt.json), [hashed index](EXP-490-direct-folds.index.json) |
| [EXP-491 PNG](EXP-491-sampled-event-sheets.png), [SVG](EXP-491-sampled-event-sheets.svg), [PDF](EXP-491-sampled-event-sheets.pdf) | [All 78 paired samples / 156 trajectories](../experiments/receipts/EXP-491-event-sheet-result.json) | [Complete figure receipt](EXP-491-sampled-event-sheets.receipt.json), [hashed index](EXP-491-sampled-event-sheets.index.json) |
| [EXP-503 PNG](EXP-503-joint-contact-residuals.png), [SVG](EXP-503-joint-contact-residuals.svg), [PDF](EXP-503-joint-contact-residuals.pdf) | [Eight fixed points, one correction, old anchor](../experiments/receipts/EXP-503-joint-contact-result.json) | [Complete figure receipt](EXP-503-joint-contact-residuals.receipt.json), [hashed index](EXP-503-joint-contact-residuals.index.json) |
| [EXP-504 PNG](EXP-504-contact-path.png), [SVG](EXP-504-contact-path.svg), [PDF](EXP-504-contact-path.pdf) | [Starting point and sole rejected continuation step](../experiments/receipts/EXP-504-contact-path-result.json) | [Complete figure receipt](EXP-504-contact-path.receipt.json), [hashed index](EXP-504-contact-path.index.json) |

EXP-504 redraw and verification (all measured points, including the rejection):

```sh
PYTHONPATH=.:python .venv/bin/python scripts/plot_exp504_contact_path.py \
  --receipt docs/experiments/receipts/EXP-504-contact-path-result.json \
  --expected-sha256 83b55c0063779f85370890ff34a04a419c475a3692dc5e3567ad4376a31ec128 \
  --output-dir artifacts/EXP-504/public-redraw
PYTHONPATH=.:python .venv/bin/python scripts/plot_exp504_contact_path.py \
  --verify-only --output-dir docs/figures
```

Redraw from public repository files, without raw target journals or new integration:

```sh
.venv/bin/python scripts/plot_exp485_transported_tangent.py \
  --receipt docs/experiments/receipts/EXP-485-transported-tangent-result.json \
  --expected-sha256 25a888fb2b75da5e99141da95072411b5099657c5030d8914a0ade10a74aed60 \
  --output-dir artifacts/EXP-485/public-redraw
```

The output directory must be new. The PNG is 300 dpi, and the SVG is vector.
Rendering/font/library changes may alter bytes; the input and per-point
derived data in the receipt provide the scientific identity. No lines are
interpolated through the observations. The displayed 1e-17-rad floor is only
a logarithmic plotting convention, not an error estimate.

EXP-486 redraw and source/code/output verification:

```sh
.venv/bin/python scripts/plot_exp486_return_image_folds.py \
  --receipt docs/experiments/receipts/EXP-486-return-image-fold-result.json \
  --expected-sha256 74fd97ef7c32e56a8c29d32113ab7cfa2531f9a48caf543906beb8cb2b5762d4 \
  --output-dir artifacts/EXP-486/public-redraw
.venv/bin/python scripts/plot_exp486_return_image_folds.py \
  --output-dir docs/figures --verify-only
```

Known unresolved brackets remain hatched gaps, not smooth connecting lines.
The gray x bands are prior candidate intervals, not uncertainty bounds.

EXP-490 redraw and verification, without raw trajectories or new integration:

```sh
.venv/bin/python scripts/plot_exp490_direct_folds.py \
  --receipt docs/experiments/receipts/EXP-490-direct-fold-result.json \
  --expected-sha256 ec74b11f2e9784ab990d142e3df36e7c500f3235faeefc92afdca50778e88b66 \
  --output-dir artifacts/EXP-490/public-redraw
.venv/bin/python scripts/plot_exp490_direct_folds.py \
  --output-dir docs/figures --verify-only
```

The outcome matrix retains unsuccessful searches and both solvers. Repeated
input x values are nearly coincident physical locations reached from different
upstream intervals, not a count of additional critical points. The figure is
not a reconstructed return curve or an all-root certificate.

EXP-491 public-data-only redraw and verification:

```sh
.venv/bin/python scripts/plot_exp491_event_sheets.py \
  --receipt docs/experiments/receipts/EXP-491-event-sheet-result.json \
  --expected-sha256 d96454454290ed83d5503fce91f9b86ccce516b40b50a84b9d35ab512f6fc879 \
  --output-dir artifacts/EXP-491/public-redraw
.venv/bin/python scripts/plot_exp491_event_sheets.py \
  --output-dir docs/figures --verify-only
```

All sixteen family panels retain three sample positions for every original
candidate and both solvers. Pointwise numerical failures or unavailable
events must not be removed. No interpolant bridges a failed interval, and
the absence of a flag at three points does not exclude hidden boundaries.

EXP-503 public-data-only redraw and verification:

```sh
PYTHONPATH=.:python .venv/bin/python -m scripts.plot_exp503_joint_contact \
  --receipt docs/experiments/receipts/EXP-503-joint-contact-result.json \
  --expected-sha256 56cf4e0d13d2f082c3272494f0ef6a4719dfd92d7d9686a74c67026c995437a7 \
  --output-dir output/pdf/EXP-503-public-redraw
PYTHONPATH=.:python .venv/bin/python -m scripts.plot_exp503_joint_contact \
  --output-dir docs/figures --verify-only
```

Both panels show the same measured residuals: one includes the two-coordinate
target, the other enlarges the observations. Means and full ranges cover all
256 correlated variants, not independent samples or confidence intervals.
Full-state contact, primitive-period and representation gates remain necessary;
the coordinate box alone cannot verify a contact or a symbolic chain. The
300-dpi PNG, vector SVG and PDF share a hashed data/code/output receipt.
