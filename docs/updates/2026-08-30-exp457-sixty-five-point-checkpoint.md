# EXP-457: sixty-five-point homoclinic checkpoint

EXP-457 passed every prospectively frozen gate in two evaluations, adding the
sixty-fifth qualified point to the Jones homoclinic continuation:

```text
(a, c) = (0.1798424282550444, 10.31700493953329)
maximum block defect = 3.1998820460207597e-9
minimum singular value = 8.443243294685767e-10
node-boundary margin = 0.9938010779404465
```

The raw receipt is 78,717 bytes with SHA-256
`d620c4024ea370d9657f580251566f2613b4a1881cdb19dedf9f0a67e0028f0f`.
The chain now contains 62 gauge-aligned pseudo-arclength roots and 65 qualified
roots overall. Forty-eight tangent-recomputed outgoing steps after EXP-408
remain smooth and interior. EXP-403 is still the sampled local `a` minimum and
the closest root to the historical `a=0.1798` section. The continued arm
therefore strengthens the nearby homoclinic-mechanism claim but does not
recover the printed coordinate or establish a later return, global
nonintersection, uniqueness, or computer-assisted existence.

EXP-458 is frozen prospectively as the first post-checkpoint successor. It
binds exact passed EXP-456/457 receipts, recomputes the tangent at EXP-457, and
retains every numerical setting and acceptance gate. A pass adds the
sixty-sixth point; a failure is preserved.
