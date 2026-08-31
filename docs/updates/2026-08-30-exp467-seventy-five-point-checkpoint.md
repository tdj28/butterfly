# EXP-467: seventy-five-point homoclinic checkpoint

EXP-467 passed every prospectively frozen gate in two evaluations, adding the
seventy-fifth qualified point to the Jones homoclinic continuation:

```text
(a, c) = (0.17985311795555772, 10.316972100406758)
maximum block defect = 3.199797489863061e-9
minimum singular value = 8.093294806532229e-10
node-boundary margin = 0.9939041000360378
```

The raw receipt is 78,682 bytes with SHA-256
`66942bb2bdd9a3b057eb6b4155edb712e24ac9109a07702fd068b9a55d1f9586`.
The chain now contains 72 gauge-aligned pseudo-arclength roots and 75 qualified
roots overall. Fifty-eight tangent-recomputed outgoing steps after EXP-408
remain smooth and interior. EXP-403 is still the sampled local `a` minimum and
the closest root to the historical `a=0.1798` section. The continued arm
therefore strengthens the nearby homoclinic-mechanism claim but does not
recover the printed coordinate or establish a later return, global
nonintersection, uniqueness, or computer-assisted existence.

The receipt-bound four-panel figure contains all 75 qualified roots and all 26
preserved failures. It was generated from clean source commit
`52362a8ddabaaad735f0a421d19867fe9b173e0e` and passed full-resolution visual
inspection:

```text
figure SHA-256  93089fb98fb170ec027f48a02f76ab297b6d7804f7c5b1b31e08d3709abcc3bd
receipt SHA-256 9ca3c7203ddf7f2ab21b71afe6181146981348f7ffba80d7f175ad637cbe6451
```

The manuscript refresh is the next checkpoint action. EXP-468 is frozen
prospectively as the first post-checkpoint
successor. It binds exact passed EXP-466/467 receipts, recomputes the tangent
at EXP-467, and retains every numerical setting and acceptance gate. A pass
adds the seventy-sixth point; a failure is preserved.
