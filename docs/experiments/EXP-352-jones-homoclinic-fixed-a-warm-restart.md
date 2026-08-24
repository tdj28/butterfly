# EXP-352 — Fixed-a homoclinic warm restart

Status: execution aborted; no scientific receipt produced

EXP-351 reduces its maximum defect from `0.0245207` to `0.000209830`
without leaving the local box, but exhausts its budget. Of 128 arc defects,
121 already pass `1e-8`; five of the seven remaining failures are concentrated
in the final five arcs adjacent to the stable target.

EXP-352 binds the exact failed receipt and restarts from all 127 fixed-`a`
internal nodes. It keeps `(a,b)=(0.1798,0.2)`, solves `c`, and changes no
physical geometry, integration tolerance, segmentation, optimization budget,
or scientific residual threshold. Only the local coordinates are recentered
on the prospectively preserved failure so that the analytic Jacobian is
relinearized there.

Manifest:
[`../../experiments/manifests/EXP-352-jones-homoclinic-fixed-a-warm-restart.json`](../../experiments/manifests/EXP-352-jones-homoclinic-fixed-a-warm-restart.json).

The clean frozen run aborts before receipt generation when an unbounded
internal-node trial causes Radau to report `Required step size is less than
spacing between numbers.` The source binding and initial evaluation succeed;
the exception occurs inside SciPy's trust-region trial. Because no terminal
residual or acceptance checks exist, EXP-352 is an execution abort, not
evidence for or against the homoclinic intersection.

The successor must add prospective source-centered component bounds to the
internal shooting nodes and expose their normalized boundary margin in the
receipt. It must otherwise bind EXP-351 again and leave the physics, solver,
budget, and `1e-8` gate unchanged.
