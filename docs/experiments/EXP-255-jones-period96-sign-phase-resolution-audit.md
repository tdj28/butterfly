# EXP-255 — Period-96 sign phase-resolution audit

Status: completed — failed administrative receipt serialization

EXP-254 passes every scientific gate except full-orbit tangent-sign identity.
Its best shift is one final grid increment from exactly one half period, and
that `7.45e-9` phase increment is too coarse for the frozen `1e-6` RMS gate on
this long orbit. EXP-255 reads the immutable corrected DOP853/Radau nodes and
uses bounded continuous scalar minimization around the already identified
half-period shift.

The `1e-6` identity threshold, 2,048 phase samples, solver profiles, endpoint
gate, and source corrected orbits are unchanged. A pass qualifies phase-shift
equivalence; a failure preserves the possibility of two nearby stable cycles.

Manifest:
[`../../experiments/manifests/EXP-255-jones-period96-sign-phase-resolution-audit.json`](../../experiments/manifests/EXP-255-jones-period96-sign-phase-resolution-audit.json).

## Result

Both continuous phase audits complete, but the script passes a NumPy boolean
to the canonical JSON writer and terminates before writing a receipt. No
scientific result is accepted under EXP-255. EXP-256 freezes a scientifically
identical successor after converting that status to a built-in boolean.
