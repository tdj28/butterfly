# Update — EXP-145 lobe/PIM overlap diagnostic frozen

EXP-144 rejects finite-horizon capture timing as a robust proxy, but leaves the
validated UPO unstable manifolds intact. A direct inverse-map stable-manifold
attempt is numerically inadmissible in Float64 because the section return is
effectively rank one.

DEC-013 therefore defines a two-dimensional overlap residual between the UPO
left escape lobe and independently reconstructed PIM saddle. EXP-145 freezes a
retrospective, hash-bound diagnostic across three PIM access lines, two censor
horizons, and nested five/nine-amplitude lobe atlases. If it passes, its only
promotion is to a prospective held-out parameter test.

## Result

EXP-145 passes all twelve access-line/horizon decisions. The two-side UPO lobe
is well populated, but the qualified PIM saddle has zero states in it on every
line. The three-side PIM saddle has 11–15 per line, all within `2.399e-5` of
the fine UPO atlas and `6.099e-5` of its nested coarse subset. This supports
lobe inclusion/pruning or reinjection retrospectively and now requires an
untouched parameter.
