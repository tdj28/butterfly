# EXP-339 — Fixed-c homoclinic single-shooting replay

Status: frozen; not yet run

EXP-338 completed its numerical optimizer but wrote no receipt because the
final initial-residual check remained a NumPy boolean. EXP-339 changes only
that value to a JSON-native boolean. The EXP-337 source row, fixed parameters,
gauge, nonlinear stable target, initial variables, local search box, DOP853
settings, optimizer tolerances and budget, root threshold, and claim limits
are unchanged.

An interior residual at most `1e-8` remains only a single-shooting root
nomination. Multiple shooting, shrinking radii, and independent integration
are mandatory before a homoclinic connection can be qualified.

Manifest:
[`../../experiments/manifests/EXP-339-jones-homoclinic-single-shooting-replay.json`](../../experiments/manifests/EXP-339-jones-homoclinic-single-shooting-replay.json).
