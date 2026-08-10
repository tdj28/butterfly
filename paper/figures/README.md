# Manuscript figures

This directory contains the publication copies used by
[the manuscript](../manuscript.tex). Figure captions preserve the project's
distinction between finite-time rasters, corrected invariant orbits, and
topology claims.

## Generated composites

- fig01-multib-superstructure.png: eleven EXP-021 fixed-\(b\) atlas frames.
- fig02-global-and-period6-zoom.png: EXP-021 global \(b=0.2\) atlas,
  EXP-192 two-landmark refinement, and the hash-bound period-6 component.
- fig08-local-period6-mesh.png: EXP-198's 2,511-point corrected-orbit mesh.
- fig07-return-map-controls.png: freshly integrated EXP-108 published
  Barrio-section controls.

Regenerate the first three and their receipt from the repository root:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=. .venv/bin/python \
      scripts/plot_paper_parameter_figures.py \
      --frame-dir artifacts/EXP-021 \
      --zoom-frame artifacts/EXP-192/frame-000.json \
      --zoom-receipt artifacts/EXP-192/frame-000.receipt.json \
      --zoom-component artifacts/EXP-192/anchor-period6-component.json \
      --local-mesh artifacts/EXP-198/candidates.json \
      --output-dir paper/figures --dpi 240

Regenerate the return-map controls and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=. .venv/bin/python \
      scripts/plot_paper_return_map_controls.py \
      --manifest experiments/manifests/EXP-108-published-return-map-controls.json \
      --receipt artifacts/EXP-108/receipt.json \
      --output paper/figures/fig07-return-map-controls.png --dpi 260

## Promoted experiment figures

The remaining images are metadata-stripped publication copies of existing
receipt-bound experiment figures:

| Manuscript file | Source experiment file | Source SHA-256 |
|---|---|---|
| fig03-hopf-locus.png | artifacts/EXP-153/rossler-hopf-curve.png | 12f3aa78a86b790895c08104c79e893e783e0f31db91d93544759ba9414a6e6c |
| fig04-hopf-family.png | artifacts/EXP-155/hopf-period1-to-hub.png | 6b61c5b83e580a95b6e5bd8b6a5508be1f92acdd5381a55c7e17b0243e5ab12d |
| fig05-flip-fold-line.png | artifacts/EXP-045/EXP-045-flip-fold-line.png | f24ac0cc3e5c94edc0b7277dec81f3d714407e8c531a169bea4396ed23f74e79 |
| fig06-flip-fold-atlas-overlay.png | artifacts/EXP-046/EXP-046-coarse-flip-fold-atlas-overlay.png | f2ae5296354d4537d0af4e54602fa99b7984f95d27ad6ca16be7e7da0a23f23c |
| fig06b-normal-form-comparison.png | artifacts/EXP-040/EXP-031-039-040-normal-form-comparison.png | 5838e807b172fcdb30254320852c68edf80451f467804409b232f86e1b9233c8 |

The EXP-038 surface image is intentionally excluded: its printed \(+1\)
event interpretation was superseded by later identity-safe \(-1\) multiplier
analysis.
