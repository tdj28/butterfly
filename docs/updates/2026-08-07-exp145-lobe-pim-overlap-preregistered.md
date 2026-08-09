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
