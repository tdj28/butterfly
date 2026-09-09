# Research-update figure receipts

This index starts with EXP-485. It is not a claim that every older figure has
the same per-figure receipt format. Older figure provenance remains in its
experiment documentation and plotting scripts.

| Figure | Audited data | Figure receipt |
| --- | --- | --- |
| [EXP-485 PNG](EXP-485-transported-tangent.png), [SVG](EXP-485-transported-tangent.svg) | [All 80 results](../experiments/receipts/EXP-485-transported-tangent-result.json) | [Inputs, derived values, code/output hashes, alt text](EXP-485-transported-tangent.receipt.json) |
| [EXP-486 PNG](EXP-486-continuous-return-curves.png), [SVG](EXP-486-continuous-return-curves.svg), [PDF](EXP-486-continuous-return-curves.pdf) | [All 16 families](../experiments/receipts/EXP-486-return-image-fold-result.json) | [Complete figure receipt](EXP-486-continuous-return-curves.receipt.json), [hashed index](EXP-486-continuous-return-curves.index.json) |

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
