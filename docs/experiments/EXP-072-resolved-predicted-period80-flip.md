# EXP-072 — Resolve the predicted period-80 flip

Status: executed; passed

Repeat only the final EXP-071 bracket using `rtol=2e-13`, `atol=2e-15`,
`max_step=0.015`, and bisection tolerance `1e-13`. Require bracket width
`<=2e-13`, multiplier residual `<=5e-9`, real multiplier, closure `<=1e-9`,
and half-period closure `>=0.001`.

The manifest preserves the original EXP-066 prediction. Passing will support
the fifth event parameter and permit the third spacing ratio and prospective
prediction error to enter the finding; it still will not prove universality or
the period-160 child.

The clean run at `eb28de1ebb4eaaa0e399206d0d460ac3fa95b0ef` passed.
It locates the period-80 `-1` event at `b=0.1797203688504993` in a
`5.03e-14` bracket. The best multiplier is `-0.99999999842`, closure is
`2.89e-12`, and half-period closure is `0.0069637`. Receipt SHA-256:
`de20ce1eaac36f0538abd3b135c05d00524ddbac2eb5914f3a8d5dff193d6f02`.

The precommitted EXP-066 prediction error is `-1.3979004e-7`, only `0.462%`
of the actual last spacing. The new spacing is `3.02525158e-5`, and the third
ratio is `4.64762654`, closer to `4.66920161` than either earlier ratio. Accept
the period-80-to-period-160 flip candidate and retain universality as a tested
hypothesis, not a conclusion. Switch and qualify the period-160 child next.
