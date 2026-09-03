# EXP-339 — Fixed-c homoclinic single-shooting replay

Status: passed execution; root unresolved by relative finite differences

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

The replay passes every source and execution check in `8.8112` seconds but
does not nominate a root. The residual decreases only from `0.00016226247` to
`0.00015881926`. The receipt shows why: SciPy perturbs the zero normalized
starting vector by about `1.49e-8`, despite the requested relative `0.001`
steps. That is too small for a 234-time-unit shooting map and yields a noisy,
nearly singular Jacobian.

EXP-340 binds this exact unresolved receipt and replaces only the relative
finite differences with explicit absolute central differences of `0.001` in
each normalized coordinate.

Tracked summary: [`receipts/EXP-339.json`](receipts/EXP-339.json). Raw receipt
SHA-256: `2a8f9433d0595bc12a5cec913adf6dbe8b5655fcbb0273412868b3953993c1cf`.
