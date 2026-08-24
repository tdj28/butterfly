# EXP-342 — Independent Radau 32-arc homoclinic correction

Status: passed; independent radius-`0.03` root reproduced

EXP-341 is a sub-`1e-8` DOP853 root nomination but is formally failed on its
termination flag, and its direct replay exhibits the expected exponential
error growth. EXP-342 binds that exact receipt and avoids long replay: each of
the 16 matched source arcs is split at a Radau-computed midpoint, producing a
32-arc Radau boundary-value seed.

The nonlinear stable target is also reconstructed with Radau. All physical
geometry, the global angle--`a`--time box, and the maximum block residual gate
remain unchanged. In addition to a sub-`1e-8` defect, the result must remain
within `5e-6` in `a`, `0.01` in angle, and `0.1` in total flight time of the
DOP853 candidate. A root satisfying those prospective gates is an independent
integrator and doubled-segmentation reproduction at radius `0.03`, not yet a
shrinking-radius homoclinic qualification or a uniqueness result.

Manifest:
[`../../experiments/manifests/EXP-342-jones-homoclinic-radau-32-segment.json`](../../experiments/manifests/EXP-342-jones-homoclinic-radau-32-segment.json).

## Result

All prospective gates pass. The initial split Radau seed already preserves the
DOP853 root at maximum block defect `2.66211e-9`; correction reduces it to
`1.08861e-9`. The final value `a=0.1826436081740286` differs from EXP-341 by
only `3.13e-11`. Angle and time differences (`0.0009494` and `0.0001872`) also
clear their frozen agreement gates by wide margins.

This is strong independent numerical support for a radius-`0.03` homoclinic
candidate at fixed `(b,c)=(0.2,10.3084)`. It does not validate Jones's printed
`a=0.1798`: the reproduced candidate lies about `0.00284361` higher. The next
decisive test keeps Radau and the 32 matched arcs while shrinking the matching
sphere; an actual connection should preserve `a` as the truncation points move
along the same invariant manifolds.

Tracked summary: [`receipts/EXP-342.json`](receipts/EXP-342.json). Raw receipt
SHA-256: `efa36db56b9dc288b973627fc588296656942dd1404191517892470761fd87b1`.
