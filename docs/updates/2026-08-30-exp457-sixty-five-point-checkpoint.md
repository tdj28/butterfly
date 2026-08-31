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

The receipt-bound four-panel figure contains all 65 qualified roots and all 26
preserved failures. It was generated from clean source commit
`a9a0f43c5d06a8af02f4aee2db293a281c8f0c09` and passed full-resolution visual
inspection:

```text
figure SHA-256  47edc8790b8ff641b5785230a83672fa06b94d304be36690aa40e0ec3bd6f319
receipt SHA-256 b86ebf8dc25a8291b7593afa213522a10cff5b73ecb519f065475cb32daa1205
```

The manuscript was rebuilt from clean source commit
`b1115a65984d978cd7f526b86297487c22587ccc`. The final PDF has 55 pages,
is 10,185,973 bytes, and has SHA-256
`778dda77be23ad2dbcdd4524e7f8a939381ba97406c8f639d41a6a274c89fe6d`.
Its log contains no undefined reference, citation, overfull-box, or
underfull-box warning. Rendered pages 1, 11, 49, 50, and 55 passed visual
inspection. All 401 tests and the 10/10/10 bibliography checks also pass.

EXP-458 is frozen prospectively as the first post-checkpoint successor. It
binds exact passed EXP-456/457 receipts, recomputes the tangent at EXP-457, and
retains every numerical setting and acceptance gate. A pass adds the
sixty-sixth point; a failure is preserved.

EXP-458 passes every unchanged gate in two evaluations at
`(a,c)=(0.1798433949843,10.3170019698684)`, with `3.19987e-9` maximum defect,
`8.39755e-10` minimum singular value, and `0.9939` node-boundary margin. The
sixty-sixth point is qualified. EXP-459 is frozen prospectively at the same
step with exact EXP-457/458 receipt bindings.

EXP-459 passes every unchanged gate in two evaluations at
`(a,c)=(0.1798443845904,10.3169989298908)`, with `3.19987e-9` maximum defect,
`8.35402e-10` minimum singular value, and `0.9940` node-boundary margin. The
sixty-seventh point is qualified. EXP-460 is frozen prospectively at the same
step with exact EXP-458/459 receipt bindings.

EXP-460 passes every unchanged gate in two evaluations at
`(a,c)=(0.1798453970758,10.3169958195927)`, with `3.19986e-9` maximum defect,
`8.31275e-10` minimum singular value, and `0.9940` node-boundary margin. The
sixty-eighth point is qualified. EXP-461 is frozen prospectively at the same
step with exact EXP-459/460 receipt bindings.
