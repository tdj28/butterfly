# EXP-337 — Fixed-c radius-0.03 a-band

Status: frozen; not yet run

EXP-336 preserves a sole coverage failure on its broad `a` domain, while its
completed rows localize a `0.00034435` chord near miss at `a=0.1828`. EXP-337
binds the exact failed receipt and failure pattern. It does not reclassify or
relax EXP-336.

The successor restricts the new scan to the observed returning band
`a in [0.1803,0.1838]`, halves spacing to `0.00025`, and enlarges the
matching sphere from `0.025` to `0.03` to improve continuous return coverage.
The fixed printed `c`, 192 angles, nonlinear stable targets, solver, horizon,
ten-percent chord gate, winding calculation, and one-time-unit continuity gate
are unchanged in meaning.

A pass requires at least 15% inward-return coverage. A continuous nonzero-
degree cell remains only a coupled-root nomination; direct proximity alone is
not sufficient.

Manifest:
[`../../experiments/manifests/EXP-337-jones-homoclinic-fixed-c-radius03-a-band.json`](../../experiments/manifests/EXP-337-jones-homoclinic-fixed-c-radius03-a-band.json).
