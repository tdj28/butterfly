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

The 55-page manuscript was then rebuilt from clean source commit
`96122564c84a375697bc9b1fda6cf90977acbf88`. The resulting 10,195,213-byte
PDF has SHA-256
`71c9f8e57c692d3a075be035c6a12d2125649ef5fc33b3740e356e9cce45f6fb`.
The build log contains no undefined references or citations and no overfull or
underfull boxes. Full-page renders of pages 1, 11, 49, 50, and 55 were visually
inspected for the abstract, continuation figure and caption, conclusion, and
bibliography. The checkpoint also passes all 401 tests and the reference audit
with 10 BibTeX entries, 10 cited keys, and all 10 required citations present.

EXP-468 is frozen prospectively as the first post-checkpoint
successor. It binds exact passed EXP-466/467 receipts, recomputes the tangent
at EXP-467, and retains every numerical setting and acceptance gate. A pass
adds the seventy-sixth point; a failure is preserved.
