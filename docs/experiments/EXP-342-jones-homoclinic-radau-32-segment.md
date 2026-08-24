# EXP-342 — Independent Radau 32-arc homoclinic correction

Status: frozen; not yet run

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
