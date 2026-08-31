# EXP-462: seventy-point homoclinic checkpoint

EXP-462 passed every prospectively frozen gate in two evaluations, adding the
seventieth qualified point to the Jones homoclinic continuation:

```text
(a, c) = (0.1798474905197595, 10.3169893885338)
maximum block defect = 3.1998415721262874e-9
minimum singular value = 8.23728082842405e-10
node-boundary margin = 0.9939980592662687
```

The raw receipt is 78,683 bytes with SHA-256
`4bf9cd03b27a49e7aacb6234ed4961a307f0c2ef11b87c866759e334e324d2f5`.
The chain now contains 67 gauge-aligned pseudo-arclength roots and 70 qualified
roots overall. Fifty-three tangent-recomputed outgoing steps after EXP-408
remain smooth and interior. EXP-403 is still the sampled local `a` minimum and
the closest root to the historical `a=0.1798` section. The continued arm
therefore strengthens the nearby homoclinic-mechanism claim but does not
recover the printed coordinate or establish a later return, global
nonintersection, uniqueness, or computer-assisted existence.

The receipt-bound four-panel figure contains all 70 qualified roots and all 26
preserved failures. It was generated from clean source commit
`baea7cc641a98c5c21b5197824586a453b4c7c45` and passed full-resolution visual
inspection:

```text
figure SHA-256  f42121325a89f753dbe253b8778f715436a21f1f7a2797897c4cc6424155d01b
receipt SHA-256 8e322213e384ec512728ea2940c02f1b54aaab143228a6e6191a69aaa1d23f3d
```

EXP-463 is frozen prospectively as the first post-checkpoint successor. It
binds exact passed EXP-461/462 receipts, recomputes the tangent at EXP-462, and
retains every numerical setting and acceptance gate. A pass adds the
seventy-first point; a failure is preserved.
