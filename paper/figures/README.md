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
- fig09-exp199-signed-residual-field.png: EXP-199's 126 cross-step-qualified
  signed critical-residual maps and normalized direct-gate distances.
- fig10-exp200-oracle-sensitivity.png: EXP-200's baseline versus high-smoothing
  branch votes under quadrupled trajectory support.
- fig11-exp201-smoothing-scale-audit.png: EXP-201's candidate qualification,
  transition brackets, and second-critical stability under nested support.
- fig12-exp202-scale-ensemble-residual-field.png: EXP-202's two signed
  scale-ensemble residual fields and normalized direct-gate obstruction.
- fig13-exp203-stable-period6-extension.png: EXP-203's qualified stable strip,
  connected components, and dominant Floquet stability margin.
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

Regenerate the EXP-199 residual field and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python .venv/bin/python \
      scripts/plot_exp199_signed_residuals.py \
      --manifest experiments/manifests/EXP-199-incomplete-local-barrio-signed-residual-scan.json \
      --receipt artifacts/EXP-199/receipt.json \
      --expected-receipt-sha256 384016b40113cfbcfbd415c514dfd52543e35c36c37132eb128f8fcd4624a4b2 \
      --output paper/figures/fig09-exp199-signed-residual-field.png --dpi 260

Regenerate the EXP-200 oracle-sensitivity field and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python .venv/bin/python \
      scripts/plot_exp200_oracle_sensitivity.py \
      --manifest experiments/manifests/EXP-200-lower-c-high-support-signed-residual-scan.json \
      --receipt artifacts/EXP-200/receipt.json \
      --expected-receipt-sha256 63199e4171c1f5a5c1fc1e309804b5f97b693567076c87ab6a94ac1b14fb4497 \
      --output paper/figures/fig10-exp200-oracle-sensitivity.png --dpi 260

Regenerate the EXP-201 smoothing-scale audit figure and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python .venv/bin/python \
      scripts/plot_exp201_smoothing_scale_audit.py \
      --manifest experiments/manifests/EXP-201-jones-critical-smoothing-scale-audit.json \
      --receipt artifacts/EXP-201/receipt.json \
      --expected-receipt-sha256 537699301785f34ad4e28c5ef682660851ea5e23af4ed7094b0164ac9078097c \
      --output paper/figures/fig11-exp201-smoothing-scale-audit.png --dpi 260

Regenerate the EXP-202 scale-ensemble residual figure and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python .venv/bin/python \
      scripts/plot_exp202_scale_ensemble_residuals.py \
      --manifest experiments/manifests/EXP-202-low-smoothing-scale-ensemble-residual.json \
      --receipt artifacts/EXP-202/receipt.json \
      --expected-receipt-sha256 11ca103e800c084431bf1283982fd8d1e55866f8a0d35f36b49ebd80e6402136 \
      --output paper/figures/fig12-exp202-scale-ensemble-residual-field.png --dpi 260

Regenerate the EXP-203 stable-period-6 extension figure and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python .venv/bin/python \
      scripts/plot_exp203_stable_period6_extension.py \
      --manifest experiments/manifests/EXP-203-lower-c-stable-period6-extension.json \
      --receipt artifacts/EXP-203/candidates.json \
      --expected-receipt-sha256 db4c841dd678e0355ff1ed1ecfb9c8d03e630ce00e4d892f2fc237d09c2e2a02 \
      --output paper/figures/fig13-exp203-stable-period6-extension.png --dpi 260

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
