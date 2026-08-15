# EXP-312 — Resume the period-3072 branch from the exact EXP-311 prefix

Status: frozen; not yet executed

EXP-311 passes all four full-step corrections and every orbit-level gate, but
the branch bends across the finite event coordinate and ends only `7.77e-13`
away. EXP-312 binds the raw EXP-311 receipt and resumes from its final two
rows. The complete five-row source prefix must be successful, retain matching
below `1e-8`, and retain primitive half-node RMS above `5e-6` before it can be
used.

The resumption permits eight pseudo-arclength corrections at nominal step
`0.000625`, with deterministic halving down to `0.00001953125` only on
correction failure. All nine resumed rows and at least `1e-11` terminal
absolute separation from the finite event coordinate are required, together
with the unchanged matching, primitive separation, terminal closure, neutral,
period-ratio, half-period nonclosure, and exact `3584/4096` identity gates.

A pass supplies farther exact period-3072 rows for a separately frozen
DOP853/Radau audit. It does not classify stability or eighth-birth direction.

Manifest:
[`../../experiments/manifests/EXP-312-jones-period3072-resumed-continuation.json`](../../experiments/manifests/EXP-312-jones-period3072-resumed-continuation.json).
