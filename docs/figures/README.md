# Research-update figure receipts

This index starts with EXP-485. It is not a claim that every older figure has
the same per-figure receipt format. Older figure provenance remains in its
experiment documentation and plotting scripts.

| Figure | Audited data | Figure receipt |
| --- | --- | --- |
| [EXP-485 PNG](EXP-485-transported-tangent.png), [SVG](EXP-485-transported-tangent.svg) | [All 80 results](../experiments/receipts/EXP-485-transported-tangent-result.json) | [Inputs, derived values, code/output hashes, alt text](EXP-485-transported-tangent.receipt.json) |

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
