# EXP-452: sixty-point homoclinic checkpoint

EXP-452 passed every prospectively frozen gate in two evaluations, adding the
sixtieth qualified point to the Jones homoclinic continuation:

```text
(a, c) = (0.17983793557436534, 10.317018739937058)
maximum block defect = 3.199918306056248e-9
minimum singular value = 8.701342755625068e-10
node-boundary margin = 0.993239973092436
```

The chain now contains 57 gauge-aligned pseudo-arclength roots and 60 qualified
roots overall. Forty-three tangent-recomputed outgoing steps after EXP-408
remain smooth and interior. EXP-403 is still the sampled local minimum and the
closest root to the historical `a=0.1798` section. The continued arm therefore
strengthens the nearby homoclinic-mechanism claim but does not recover the
printed coordinate or establish a later return, global nonintersection,
uniqueness, or computer-assisted existence.

The receipt-bound four-panel figure includes all 60 roots and all 26 preserved
failures. It is bound to clean source commit
`e14e93be53121453e3cf662da3838ff2e62415ad`:

```text
figure SHA-256  3c2b55b4eda70a0780743ae71d374d9b51aa8b68e6d8b2c890a113c1b1de019d
receipt SHA-256 b6696138174ae222affe9344a20c29b55bbdd5cf5e5ec7a60edfafb31b4155ee
```

The rebuilt 55-page manuscript is 10,194,114 bytes with SHA-256
`de21b457dcccde098b3fa64c75e9e58518e2484bcb8c42b33f6b289c27404df1`.
Its log has no undefined reference, citation, overfull-box, or underfull-box
warning. Rendered pages 1, 11, 49, and 50 and the full-resolution source figure
passed visual inspection. All 401 tests and the 10/10/10 bibliography checks
also pass.
