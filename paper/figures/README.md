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
- fig14-exp205-period6-flip-curve.png: EXP-205's seven refined real-minus-one
  period-6 Floquet events over the EXP-203 field and their sign brackets.
- fig15-exp206-period6-flip-continuation.png: EXP-206's 41-point coupled flip
  curve, event-period variation, and residual-quality controls.
- fig16-exp208-period12-children.png: EXP-208's three sampled children,
  parent/child stability exchange, and proper-subperiod rejection.
- fig17-exp209-period12-normal-form.png: EXP-209's square-root child opening,
  multiplier-ratio scaling, and two-sided perturbed-attraction checks.
- fig18-exp211-period12-surface.png: EXP-211's 124-point child sheet, 31
  square-root fits, stability exchange, and recovery of EXP-210's 16
  doubled-parent collapses.
- fig19-exp212-214-flip-extension-grazing.png: EXP-212's broad parent-curve
  extension and EXP-213/214's continuous, extremum-aware qualification of a
  seven-to-six historical-section grazing.
- fig20-exp215-217-folded-flip-locus.png: the qualified passage through that
  grazing, lower-`c` projection turn, 135-point returning arm, widening
  two-arm separation, and strict residual audit.
- fig21-exp223-226-returning-child-endpoint.png: the 45-event returning-arm
  stable child strip, its recrossing of the known flip arm, the bilateral
  primitive-child versus parent-double-cover audit, and EXP-229's correction
  of the former interpolation-based distinct-boundary interpretation.
- fig22-exp237-275-returning-cascade.png: six exact returning-arm flip events,
  four finite spacing ratios, and two-solver supercritical stability exchange
  through a stable primitive period-768 child.
- fig25-exp316-320-birth-criticality.png: resolution-doubled quadratic opening
  and stable immediate daughters at the supercritical seventh birth, plus the
  stable-parent/unstable-daughter evidence for the subcritical eighth birth.
- fig26-exp324-325-target-collapse.png: matching, primitive amplitude, Armijo
  factors, and phase-space convergence for the independently repeated
  4,096/8,192-step collapse of the old EXP-299 seed to its doubled parent.
- fig27-exp321-327-sheet-connection.png: exact daughter continuation through
  event eight, signed real-`-1` crossing, shared-phase identity convergence,
  and normalized gate margins.
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

Regenerate the EXP-205 period-6 flip-curve figure and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python .venv/bin/python \
      scripts/plot_exp205_period6_flip_curve.py \
      --manifest experiments/manifests/EXP-205-lower-c-period6-flip-refinement.json \
      --field artifacts/EXP-203/candidates.json \
      --expected-field-sha256 db4c841dd678e0355ff1ed1ecfb9c8d03e630ce00e4d892f2fc237d09c2e2a02 \
      --receipt artifacts/EXP-205/receipt.json \
      --expected-receipt-sha256 42580233a066dc3dee8766f7fab75202ff4594b99cd74f0047e9966a0af22ee0 \
      --output paper/figures/fig14-exp205-period6-flip-curve.png --dpi 260

Regenerate the EXP-206 coupled flip-curve figure and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python .venv/bin/python \
      scripts/plot_exp206_period6_flip_curve.py \
      --manifest experiments/manifests/EXP-206-lower-c-period6-flip-curve.json \
      --field artifacts/EXP-203/candidates.json \
      --expected-field-sha256 db4c841dd678e0355ff1ed1ecfb9c8d03e630ce00e4d892f2fc237d09c2e2a02 \
      --source-receipt artifacts/EXP-205/receipt.json \
      --expected-source-sha256 42580233a066dc3dee8766f7fab75202ff4594b99cd74f0047e9966a0af22ee0 \
      --receipt artifacts/EXP-206/receipt.json \
      --expected-receipt-sha256 e0ced2227c7074ea5eec55ff191159d80bc43216b8f2d5826c1cfe645f3708ba \
      --output paper/figures/fig15-exp206-period6-flip-continuation.png --dpi 260

Regenerate the EXP-208 period-12 child-qualification figure and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python .venv/bin/python \
      scripts/plot_exp208_period12_children.py \
      --manifest experiments/manifests/EXP-208-qualify-period12-children.json \
      --curve-receipt artifacts/EXP-206/receipt.json \
      --expected-curve-sha256 e0ced2227c7074ea5eec55ff191159d80bc43216b8f2d5826c1cfe645f3708ba \
      --receipt artifacts/EXP-208/receipt.json \
      --expected-receipt-sha256 dbe0bc6cfffdc39b7b2e7f7e1d967cbb2662871a388861d318f8ce781b0f7e69 \
      --output paper/figures/fig16-exp208-period12-children.png --dpi 260

Regenerate the EXP-209 normal-form and attraction figure and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python .venv/bin/python \
      scripts/plot_exp209_period12_normal_form.py \
      --manifest experiments/manifests/EXP-209-period12-normal-form.json \
      --receipt artifacts/EXP-209/receipt.json \
      --expected-receipt-sha256 f57becaf08aa0ddb7a05bd7e258448cc95f3aca7611ebcd4cf00265303ebbfd0 \
      --output paper/figures/fig17-exp209-period12-normal-form.png --dpi 260

Regenerate the EXP-211 period-12 surface figure and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python:. .venv/bin/python \
      scripts/plot_exp211_period12_surface.py \
      --manifest experiments/manifests/EXP-211-period12-surface-recovery.json \
      --failed-receipt artifacts/EXP-210/receipt.json \
      --expected-failed-sha256 4f9c5885d91754a29ac59d2d0bdfae7916f7a19d5d91ea91ff797fc1ccb211ce \
      --receipt artifacts/EXP-211/receipt.json \
      --expected-receipt-sha256 1e706b3c331c6261a358681ab127063c123fe8e30ba2e7ab24ee6a301edb9249 \
      --output paper/figures/fig18-exp211-period12-surface.png --dpi 260

Regenerate the EXP-212--214 flip-extension and grazing figure and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python:. .venv/bin/python \
      scripts/plot_exp212_214_flip_extension_grazing.py \
      --curve-receipt artifacts/EXP-206/receipt.json \
      --expected-curve-sha256 e0ced2227c7074ea5eec55ff191159d80bc43216b8f2d5826c1cfe645f3708ba \
      --extension-receipt artifacts/EXP-212/receipt.json \
      --expected-extension-sha256 a322c78612874a3735a169e647c66aaa4fdddf81397d39d691ecc6c6e7ec04f1 \
      --grazing-receipt artifacts/EXP-213/receipt.json \
      --expected-grazing-sha256 7abc822a5683646e8dba007c2f34801762eb1f6ecdba8442e5217f9f41099b9f \
      --count-receipt artifacts/EXP-214/receipt.json \
      --expected-count-sha256 9ab2233c6f78a5a77d41b8912d45fd1387ea99c0816cabd0086379b2ec77510a \
      --output paper/figures/fig19-exp212-214-flip-extension-grazing.png --dpi 260

Regenerate the EXP-215--217 folded flip-locus figure and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python:. .venv/bin/python \
      scripts/plot_exp215_217_folded_flip_locus.py \
      --curve-receipt artifacts/EXP-206/receipt.json \
      --expected-curve-sha256 e0ced2227c7074ea5eec55ff191159d80bc43216b8f2d5826c1cfe645f3708ba \
      --child-receipt artifacts/EXP-211/receipt.json \
      --expected-child-sha256 1e706b3c331c6261a358681ab127063c123fe8e30ba2e7ab24ee6a301edb9249 \
      --extension-receipt artifacts/EXP-212/receipt.json \
      --expected-extension-sha256 a322c78612874a3735a169e647c66aaa4fdddf81397d39d691ecc6c6e7ec04f1 \
      --grazing-receipt artifacts/EXP-213/receipt.json \
      --expected-grazing-sha256 7abc822a5683646e8dba007c2f34801762eb1f6ecdba8442e5217f9f41099b9f \
      --through-receipt artifacts/EXP-215/receipt.json \
      --expected-through-sha256 43488e68c43e6873ce1240f44d609c7a259fa1502d09ed6fb72946fdea346c3c \
      --turn-receipt artifacts/EXP-216/receipt.json \
      --expected-turn-sha256 c0dfcfc02153da3066e4e1198dd1a8ce9ada902c78afa4d584ab1c469b75f2e5 \
      --returning-receipt artifacts/EXP-217/receipt.json \
      --expected-returning-sha256 b2ae896f075fc14c5cc580dc657611b041e62dce6eaf44a2da9b155ad39f3b65 \
      --output paper/figures/fig20-exp215-217-folded-flip-locus.png --dpi 260

Regenerate the EXP-223--226 returning-child endpoint figure and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python:. .venv/bin/python \
      scripts/plot_exp223_226_returning_child_endpoint.py \
      --event-receipt artifacts/EXP-217/receipt.json \
      --expected-event-sha256 b2ae896f075fc14c5cc580dc657611b041e62dce6eaf44a2da9b155ad39f3b65 \
      --adaptive-receipt artifacts/EXP-223/receipt.json \
      --expected-adaptive-sha256 1ee1f5c4c59e15403b06c745e5c66ce64944f01700d02bfb54fafb2a86dd1782 \
      --endpoint-receipt artifacts/EXP-226/receipt.json \
      --expected-endpoint-sha256 59c30304622fb842f5017d86ff804a1ae5f9f966e2b2f5fac4ee9d1e80d56251 \
      --identity-receipt artifacts/EXP-229/receipt.json \
      --expected-identity-sha256 d09dce1e02a24d06279e30cb5bb8e2c5f19b28af56cdbeb8ce0c8ad46afe5efa \
      --output paper/figures/fig21-exp223-226-returning-child-endpoint.png --dpi 260

Regenerate the EXP-237--269 returning-arm cascade figure and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python:. .venv/bin/python \
      scripts/plot_exp237_275_returning_cascade.py \
      --event12-receipt artifacts/EXP-237/receipt.json \
      --expected-event12-sha256 088258b0c0cca6f5cb847ced26ff44dff00a6c67bdd50858d4f504e45f4e2cba \
      --qual24-receipt artifacts/EXP-241/receipt.json \
      --expected-qual24-sha256 5ff13b1b705e15bf1dd68dbd78e788e863aab1981a7c8580b9945bec32f2aee6 \
      --event24-receipt artifacts/EXP-244/receipt.json \
      --expected-event24-sha256 9c3579c86500998daca262dda77b480beaaee913ab3089767bea3a20102defba \
      --qual48-receipt artifacts/EXP-246/receipt.json \
      --expected-qual48-sha256 eaccf68656f8aa856299c934a0a41c61ea28a4ae3d9ac7eea1c81fc20067dc52 \
      --event48-receipt artifacts/EXP-251/receipt.json \
      --expected-event48-sha256 db095fb0f303aee1d39418024517958b8b514e949ba6b82233eed49241cac2f5 \
      --qual96-receipt artifacts/EXP-253/receipt.json \
      --expected-qual96-sha256 6d084dea91779dd49e9ceb92918915ca278543db37de7c8130c076321ca8be7f \
      --event96-receipt artifacts/EXP-259/receipt.json \
      --expected-event96-sha256 189d4ba3b89b93611456a68c3c0a6ea793b151ebf7bc7bedaa8bc09a655cb3be \
      --qual192-receipt artifacts/EXP-261/receipt.json \
      --expected-qual192-sha256 70e5b63627408a8fce360bbff5c4375d40b277f82a70c1c599645494473de732 \
      --event192-receipt artifacts/EXP-267/receipt.json \
      --expected-event192-sha256 b2ae9d6ec1ecdd56de14d9c97a7a6dd56d444f6d4ace9dc1ea35a9be851243dd \
      --qual384-receipt artifacts/EXP-269/receipt.json \
      --expected-qual384-sha256 3136e119680f9b0e4e6f7a6a42f5eba7c89b5ff7a8c1e2b2ae22930a8e15ce65 \
      --event384-receipt artifacts/EXP-273/receipt.json \
      --expected-event384-sha256 31f1fd0d2db4ca9b58909e9eda14b4a5c41a382f98647feb27114921d211d265 \
      --qual768-receipt artifacts/EXP-275/receipt.json \
      --expected-qual768-sha256 98a47619175a39aa776f3a4c82234d94019ca3d9e766ff525613378035544e61 \
      --output paper/figures/fig22-exp237-275-returning-cascade.png --dpi 260

Regenerate the EXP-324/325 target-collapse figure and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python:. .venv/bin/python \
      scripts/plot_exp324_325_target_collapse.py \
      --exp324 artifacts/EXP-324/receipt.json \
      --exp324-sha256 c077aeaa23ca74fd64fc74f98d39ca7ad6ba81a255955ccf87647f3a0bf233e6 \
      --exp325 artifacts/EXP-325/receipt.json \
      --exp325-sha256 352b2254cca632f644b8c55b236d6f4487801e9223e87810eb3db4596e7cfbcc \
      --output paper/figures/fig26-exp324-325-target-collapse.png --dpi 260

Regenerate the EXP-321/326/327 sheet-connection figure and receipt:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python:. .venv/bin/python \
      scripts/plot_exp321_327_sheet_connection.py \
      --exp321 artifacts/EXP-321/receipt.json \
      --exp321-sha256 09dc671c78489d38d90d08c1c89458a247fbe51a04582bf3775e2ed6a7e6989a \
      --exp326 artifacts/EXP-326/receipt.json \
      --exp326-sha256 f94a3c63dad90c729138c4902b5af44d7194bda42dd18c42f730737f640ff89f \
      --exp327 artifacts/EXP-327/receipt.json \
      --exp327-sha256 c9ec92bd735fb8460ed0e7986ef07102943ff2032261c0c72edabcfa6b54d9c9 \
      --output paper/figures/fig27-exp321-327-sheet-connection.png --dpi 260

Regenerate the EXP-342--432 homoclinic-continuation figure and receipt from
the compact, repository-bound experiment summaries:

    MPLCONFIGDIR=/tmp/butterfly-mpl PYTHONPATH=python:. .venv/bin/python \
      scripts/plot_exp342_382_homoclinic_continuation.py \
      --receipt-dir docs/experiments/receipts \
      --output paper/figures/fig30-exp342-382-homoclinic-continuation.png \
      --receipt paper/figures/fig30-exp342-382-homoclinic-continuation.png.receipt.json \
      --dpi 260

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
